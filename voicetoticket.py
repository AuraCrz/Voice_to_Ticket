import json
import uuid
from datetime import datetime
import time
from pathlib import Path

import openai, os
import dotenv

dotenv.load_dotenv()

from langdetect import detect, LangDetectException
from deep_translator import GoogleTranslator
import speech_recognition as sr

# ----- Configuración Idioma -----
from config import LANG_NOMBRES, load_config, configurar

settings = load_config()
LANG_SISTEMA = settings.get("idioma_iso", "es")


def reconfigurar():
    '''Actualiza settings y LANG_SISTEMA en memoria tras cambio de idioma.'''
    global settings, LANG_SISTEMA
    settings = configurar()
    LANG_SISTEMA = settings.get("idioma_iso", "es")


# ----- Configuración Capa LLM -----
API_KEY = os.getenv("API_KEY")
MODEL   = "gpt-4o-mini"
DB_FILE = Path("incidents.json")

client = openai.OpenAI(api_key=API_KEY)


# ----- Persistencia -----

def cargar_incidentes() -> list[dict]:
    '''Lee incidents.json y retorna la lista de incidentes. Retorna [] si no existe.'''
    if DB_FILE.exists():
        return json.loads(DB_FILE.read_text(encoding="utf-8"))
    return []


def guardar_incidentes(incidentes: list[dict]) -> None:
    '''Escribe la lista de incidentes al archivo JSON.'''
    DB_FILE.write_text(
        json.dumps(incidentes, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ----- Capa gratuita: idioma + traducción -----

def detectar_idioma(texto: str) -> str:
    '''Retorna el código ISO-639-1 del idioma detectado en el texto.'''
    try:
        return detect(texto)
    except LangDetectException:
        return "desconocido"


def traducir_a_espanol(texto: str, idioma_origen: str) -> str:
    '''Traduce texto al español. Si ya está en español, lo retorna sin cambios.'''
    if idioma_origen == LANG_SISTEMA:
        return texto
    try:
        return GoogleTranslator(source=idioma_origen, target="es").translate(texto)
    except Exception as e:
        print(f"  [!] No se pudo traducir: {e}")
        return texto


# ----- Transcripción de voz -----

def transcripcion_voz(timeout_espera=5, tiempo_maximo=15, idioma_voz="es-MX") -> dict:
    '''
    Graba audio del micrófono y lo transcribe con Google Speech.
    Retorna dict con keys: status, texto, duracion (y error si aplica).
    '''
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 1.0

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("  Escuchando...")
            inicio = time.time()
            audio = recognizer.listen(
                source,
                timeout=timeout_espera,
                phrase_time_limit=tiempo_maximo,
            )

        texto = recognizer.recognize_google(audio, language=idioma_voz)
        return {
            "status"  : "success",
            "texto"   : texto,
            "duracion": round(time.time() - inicio, 2),
        }

    except sr.WaitTimeoutError:
        return {"status": "timeout",      "texto": "", "duracion": 0}
    except sr.UnknownValueError:
        return {"status": "no_entendido", "texto": "", "duracion": 0}
    except sr.RequestError as e:
        return {"status": "error_api",    "texto": "", "duracion": 0, "error": str(e)}
    except Exception as e:
        return {"status": "error",        "texto": "", "duracion": 0, "error": str(e)}


# ----- Capa LLM -----

def analizar_incidente(texto_es: str) -> dict:
    '''
    Envía el texto (ya en español) al LLM y retorna JSON con:
    categoria, severidad, resumen.
    '''
    prompt = """Eres un sistema de gestión de incidentes corporativos.
El texto ya está en español. Analízalo y responde ÚNICAMENTE con JSON válido
(sin bloques de código, sin explicaciones adicionales):
{
    "categoria": "<Técnico | Seguridad | Operacional | RR.HH. | Infraestructura | Otro>",
    "severidad": "<baja | media | alta | critica>",
    "resumen":   "<resumen del incidente en máximo 30 palabras>"
}""".strip()

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user",   "content": texto_es},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content.strip())


# ----- Helpers de entrada -----

def _obtener_texto_escrito() -> str:
    '''Solicita texto por teclado. Repite hasta recibir algo no vacío.'''
    while True:
        texto = input("  Describa el incidente:\n  > ").strip()
        if texto:
            return texto
        print("  [!] El texto no puede estar vacío. Intenta de nuevo.")


def _obtener_texto_voz() -> tuple[str, dict]:
    '''
    Graba audio y presenta el bucle de confirmación al usuario.
    Retorna (texto_final, voice_dict) o lanza SystemExit si cancela.
    En edición manual detecta el idioma del texto editado.
    '''
    idioma_voz = settings.get("idioma_voz", "es-MX")
    voice      = transcripcion_voz(idioma_voz=idioma_voz)
    texto      = voice.get("texto", "").strip()

    while True:
        if not texto:
            print("  [!] No se pudo obtener texto.")
            print("\n  ¿Qué deseas hacer?")
            print("  [r] Regrabar")
            print("  [n] Cancelar")
            eleccion = input("\n  Opción: ").strip().lower()

            if eleccion == "r":
                voice = transcripcion_voz(idioma_voz=idioma_voz)
                texto = voice.get("texto", "").strip()
            elif eleccion == "n":
                print("  Reporte cancelado.")
                return None, None
            else:
                print("  Opción no válida.")

        else:
            print(f"\n  Texto reconocido: {texto}")
            print("\n  ¿Qué deseas hacer?")
            print("  [s] Continuar")
            print("  [r] Regrabar")
            print("  [e] Editar manualmente")
            print("  [n] Cancelar")
            eleccion = input("\n  Opción: ").strip().lower()

            if eleccion == "s":
                return texto, voice

            elif eleccion == "r":
                voice = transcripcion_voz(idioma_voz=idioma_voz)
                texto = voice.get("texto", "").strip()

            elif eleccion == "e":
                print(f"  Texto actual: {texto}")
                editado = input("  Editar: ").strip()
                if editado:
                    # Texto editado manualmente: se detecta su idioma real
                    texto = editado
                    voice["editado"] = True
                else:
                    print("  [!] Texto vacío, se mantiene el anterior.")

            elif eleccion == "n":
                print("  Reporte cancelado.")
                return None, None

            else:
                print("  Opción no válida.")


# ----- Flujo principal -----

def registrar_incidente(voz=False):
    '''Registra un nuevo incidente por texto escrito o dictado por voz.'''
    print("\n" + "═" * 60)
    print("  NUEVO REPORTE DE INCIDENTE")
    print("═" * 60)

    voice = None

    if not voz:
        texto         = _obtener_texto_escrito()
        codigo_idioma = detectar_idioma(texto)
    else:
        texto, voice = _obtener_texto_voz()
        if texto is None:
            return

        # Si fue editado manualmente, detectar idioma real del texto editado
        if voice.get("editado"):
            codigo_idioma = detectar_idioma(texto)
        else:
            codigo_idioma = settings.get("idioma_iso", "es")

    nombre_idioma = LANG_NOMBRES.get(codigo_idioma, codigo_idioma.upper())

    # Traducción a español si es necesario
    if codigo_idioma != "es":
        print("  Traduciendo al español...")
        texto_es = traducir_a_espanol(texto, codigo_idioma)
        print(f"  Texto en español: {texto_es}")
    else:
        texto_es = texto

    # Análisis con LLM
    print("\n  Analizando incidente...")
    analisis = analizar_incidente(texto_es)

    sev_icon = {"baja": "🟢", "media": "🟡", "alta": "🟠", "critica": "🔴"}.get(
        analisis.get("severidad", ""), "⚪"
    )

    print(f"\n{'─' * 60}")
    print(f"  Categoría : {analisis['categoria']}")
    print(f"  {sev_icon} Severidad : {analisis['severidad'].upper()}")
    print(f"  Resumen   : {analisis['resumen']}")
    print(f"{'─' * 60}")

    # Guardar
    guardar = input("\n  ¿Guardar este reporte? (s/no): ").strip().lower()
    if guardar in ("s", "si", "sí", "y", "yes"):
        incidente = {
            "id"            : str(uuid.uuid4())[:8],
            "timestamp"     : datetime.now().isoformat(timespec="seconds"),
            "fuente"        : "voz" if voz else "teclado",
            "texto_original": texto,
            "voz_duracion"  : voice.get("duracion") if voice else None,
            "voz_status"    : voice.get("status")   if voice else None,
            "idioma_codigo" : codigo_idioma,
            "idioma_nombre" : nombre_idioma,
            "texto_es"      : texto_es,
            "categoria"     : analisis["categoria"],
            "severidad"     : analisis["severidad"],
            "resumen"       : analisis["resumen"],
        }
        incidentes = cargar_incidentes()
        incidentes.append(incidente)
        guardar_incidentes(incidentes)
        print(f"\n  Reporte guardado — ID: {incidente['id']}")
    else:
        print("  Reporte descartado.")


def listar_incidentes():
    '''Muestra todos los incidentes registrados con formato visual.'''
    incidentes = cargar_incidentes()
    if not incidentes:
        print("\n  No hay incidentes registrados.")
        return

    print(f"\n{'═' * 60}")
    print(f"  INCIDENTES REGISTRADOS ({len(incidentes)} total)")
    print(f"{'═' * 60}")

    for inc in incidentes:
        sev_icon = {"baja": "🟢", "media": "🟡", "alta": "🟠", "critica": "🔴"}.get(
            inc.get("severidad", ""), "⚪"
        )
        fuente = "🎙" if inc.get("fuente") == "voz" else "⌨"
        print(f"\n  [{inc['id']}] {inc['timestamp']} {fuente}")
        print(f"  {sev_icon} {inc['severidad'].upper()} | {inc['categoria']} | {inc['idioma_nombre']}")
        print(f"  {inc['resumen']}")

    print(f"\n{'─' * 60}")


def menu():
    '''Muestra el menú principal y despacha las opciones del usuario.'''
    # Garantizar configuración válida antes de mostrar el menú
    global settings
    if not settings:
        settings = configurar()

    print("\n" + "═" * 60)
    print("  SISTEMA DE REPORTES DE INCIDENTES")
    print("═" * 60)

    opciones = {
        "1": ("Registrar nuevo incidente",              lambda: registrar_incidente(voz=False)),
        "2": ("Registrar nuevo incidente con micrófono",lambda: registrar_incidente(voz=True)),
        "3": ("Ver incidentes registrados",             listar_incidentes),
        "4": ("Configurar idioma del sistema",          reconfigurar),
        "5": ("Salir",                                  None),
    }

    while True:
        print()
        for k, (desc, _) in opciones.items():
            print(f"  [{k}] {desc}")
        eleccion = input("\n  Opción: ").strip()

        if eleccion == "5":
            print("\n  Hasta luego.\n")
            break
        elif eleccion in opciones:
            opciones[eleccion][1]()
        else:
            print("  Opción no válida.")


if __name__ == "__main__":
    menu()