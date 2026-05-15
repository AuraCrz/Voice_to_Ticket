import json
import uuid
from datetime import datetime
import time
from pathlib import Path

import openai, os # LLM
import dotenv      # Carga variables de entorno desde .env

dotenv.load_dotenv()

# Dependencias gratuitas para idioma, traducción y transcripción de voz
from langdetect import detect, LangDetectException
from deep_translator import GoogleTranslator
import speech_recognition as sr

# ----- Configuración -----
API_KEY      = os.getenv("API_KEY")
MODEL        = "gpt-4o-mini"
DB_FILE      = Path("incidents.json")
LANG_SISTEMA = "es"                 # ISO-639-1: idioma base del sistema

LANG_NOMBRES = {                    # códigos ISO → nombres legibles
    "es": "Español",  "en": "Inglés",    "fr": "Francés",
    "de": "Alemán",   "pt": "Portugués", "it": "Italiano",
    "zh": "Chino",    "ja": "Japonés",   "ar": "Árabe",
    "ru": "Ruso",     "ko": "Coreano",   "nl": "Holandés",
    "pl": "Polaco",   "tr": "Turco",     "hi": "Hindi",
}

client = openai.OpenAI(api_key=API_KEY)

# ----- Persistencia -----
# Lee el JSON existente o retorna lista vacía si no hay archivo.
def cargar_incidentes() -> list[dict]:
    if DB_FILE.exists():
        return json.loads(DB_FILE.read_text(encoding="utf-8"))
    return []

# Escribe la lista de incidentes al archivo en formato JSON legible.
def guardar_incidentes(incidentes: list[dict]) -> None:
    DB_FILE.write_text(
        json.dumps(incidentes, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

# ----- Capa gratuita: idioma + traducción -----

# Retorna el idioma (código ISO-639-1).
def detectar_idioma(texto: str) -> str:
    try:
        return detect(texto)
    except LangDetectException:
        return "desconocido"


# Traduce al español usando Google Translate
def traducir_a_espanol(texto: str, idioma_origen: str) -> str:
    if idioma_origen == LANG_SISTEMA:
        return texto
    try:
        return GoogleTranslator(source=idioma_origen, target=LANG_SISTEMA).translate(texto)
    except Exception as e:
        print(f"No se pudo traducir automáticamente: {e}")
        return texto   

# Traduce a cualquier idioma
def traducir_a_idioma(texto: str, idioma_destino: str) -> str:
    try:
        return GoogleTranslator(source=LANG_SISTEMA, target=idioma_destino).translate(texto)
    except Exception as e:
        return f"[Error de traducción: {e}]"

# Transcribe voz a texto usando SpeechRecognition y Google Web Speech API
def transcripcion_voz(timeout_espera=5, tiempo_maximo=15):
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 1.0

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Escuchando...")
            inicio = time.time()
            audio = recognizer.listen(
                source,
                timeout=timeout_espera,
                phrase_time_limit=tiempo_maximo
            )

        texto = recognizer.recognize_google(audio)

        return {
            "status": "success",
            "texto": texto,
            "duracion": round(time.time() - inicio, 2)
        }

    except sr.WaitTimeoutError:
        return {
            "status": "timeout",
            "texto": "",
            "duracion": 0
        }

    except sr.UnknownValueError:
        return {
            "status": "no_entendido",
            "texto": "",
            "duracion": 0
        }

    except sr.RequestError as e:
        return {
            "status": "error_api",
            "texto": "",
            "error": str(e),
            "duracion": 0
        }

    except Exception as e:
        return {
            "status": "error",
            "texto": "",
            "error": str(e),
            "duracion": 0
        }

# ----- Capa LLM: solo análisis del incidente (texto ya en español) -----
''' El prompt ya traducido al español, es procesado por el modelo para extraer:
- categoria  : tipo de incidente
- severidad  : baja | media | alta | critica
- resumen    : <= 30 palabras'''
def analizar_incidente(texto_es: str) -> dict:
    prompt = """ Eres un sistema de gestión de incidentes corporativos.
                El texto ya está en español. Analízalo y responde ÚNICAMENTE con JSON válido
                (sin bloques de código, sin explicaciones adicionales):
                {
                    "categoria": "<Técnico | Seguridad | Operacional | RR.HH. | Infraestructura | Otro>",
                    "severidad": "<baja | media | alta | critica>",
                    "resumen":   "<resumen del incidente en máximo 30 palabras>"
                }
                """.strip()

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


# ----- Flujo principal -----
def registrar_incidente(voz=False):
    print("\n" + "═" * 60)
    print("  NUEVO REPORTE DE INCIDENTE")
    print("═" * 60)

    # Entrada de texto o voz
    if not voz:
        texto = input("Describe el incidente (en cualquier idioma):\n> ").strip()
    else:
        voice_text = transcripcion_voz()
        status = voice_text.get("status", "")
        texto = voice_text.get("texto", "")
        duracion = voice_text.get("duracion", 0)
        if not texto:
            print("[!] No se pudo obtener texto. Cancelado.")
            return
        else:
            print(f"  Texto reconocido: {texto}")
            continuar = input("Continuar? (s/n): ").strip().lower()
            if continuar not in ("s", "si", "sí", "y", "yes"):
                print("  Reporte cancelado por el usuario.")
                return
       

    # Detección de idioma 
    codigo_idioma  = detectar_idioma(texto)
    nombre_idioma  = LANG_NOMBRES.get(codigo_idioma, codigo_idioma.upper())
    print(f"\n  Idioma detectado : {nombre_idioma} ({codigo_idioma})")

    # Traducción a español si es necesario 
    if codigo_idioma != LANG_SISTEMA:
        print(" Traduciendo al español...")
        texto_es = traducir_a_espanol(texto, codigo_idioma)
        print(f" Texto en español : {texto_es}")
    else:
        texto_es = texto

    # Análisis con LLM
    print("\n  Analizando incidente...")
    analisis = analizar_incidente(texto_es)

    sev_icon = {"baja": "🟢", "media": "🟡", "alta": "🟠", "critica": "🔴"}.get(
        analisis.get("severidad", ""), "⚪"
    )

    print(f"\n{'─'*60}")
    print(f"  Categoría : {analisis['categoria']}")
    print(f"  {sev_icon} Severidad : {analisis['severidad'].upper()}")
    print(f"  Resumen   : {analisis['resumen']}")
    print(f"{'─'*60}")

    #Implementarlo en el futuro junto a un boton para traducir el resumen a otros idiomas, si el usuario lo desea.
    '''
    # Traducción adicional opcional
    opcion = input("\n¿Deseas ver el resumen en otro idioma? (s/no): ").strip().lower()
    if opcion in ("s", "si", "sí", "y", "yes"):
        idioma_extra = input(
            "Código de idioma destino (ej. en=inglés, fr=francés, de=alemán): "
        ).strip().lower()
        traduccion_extra = traducir_a_idioma(analisis["resumen"], idioma_extra)
        print(f"  → {traduccion_extra}")
    '''

    # Guardar
    guardar = input("\n¿Guardar este reporte? (s/no): ").strip().lower()
    if guardar in ("s", "si", "sí", "y", "yes"):
        incidente = {
            "id"             : str(uuid.uuid4())[:8],
            "timestamp"      : datetime.now().isoformat(timespec="seconds"),
            "texto_original" : texto,
            "voz_duracion"   : duracion if voz else None,
            "voz_status"     : status if voz else None,
            "idioma_codigo"  : codigo_idioma,
            "idioma_nombre"  : nombre_idioma,
            "texto_es"       : texto_es,
            "categoria"      : analisis["categoria"],
            "severidad"      : analisis["severidad"],
            "resumen"        : analisis["resumen"],
        }
        incidentes = cargar_incidentes()
        incidentes.append(incidente)
        guardar_incidentes(incidentes)
        print(f"\n  Reporte guardado — ID: {incidente['id']}")
    else:
        print("  Reporte descartado.")


def listar_incidentes():
    incidentes = cargar_incidentes()
    if not incidentes:
        print("\n  No hay incidentes registrados.")
        return

    print(f"\n{'═'*60}")
    print(f"  INCIDENTES REGISTRADOS ({len(incidentes)} total)")
    print(f"{'═'*60}")
    for inc in incidentes:
        sev_icon = {"baja": "🟢", "media": "🟡", "alta": "🟠", "critica": "🔴"}.get(
            inc.get("severidad", ""), "⚪"
        )
        print(f"\n  [{inc['id']}] {inc['timestamp']}")
        print(f"  {sev_icon} {inc['severidad'].upper()} | {inc['categoria']} | {inc['idioma_nombre']}")
        print(f"  {inc['resumen']}")
    print(f"\n{'─'*60}")


def menu():
    print("\n" + "═" * 60)
    print("  SISTEMA DE REPORTES DE INCIDENTES ")
    print("═" * 60)

    opciones = {
        "1": ("Registrar nuevo incidente",  lambda: registrar_incidente(voz=False)),
        "2": ("Registrar nuevo incidente con micrófono", lambda: registrar_incidente(voz=True)),
        "3": ("Ver incidentes registrados", listar_incidentes),
        "4": ("Salir",                      None),
    }

    while True:
        print()
        for k, (desc, _) in opciones.items():
            print(f"  [{k}] {desc}")
        eleccion = input("\n  Opción: ").strip()

        if eleccion == "4":
            print("\n  Hasta luego.\n")
            break
        elif eleccion in opciones:
            opciones[eleccion][1]()
        else:
            print("  Opción no válida.")


if __name__ == "__main__":
    menu()