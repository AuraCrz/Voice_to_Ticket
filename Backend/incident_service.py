import json
import uuid
from datetime import datetime
from pathlib import Path
import os
import dotenv
import openai

from langdetect import detect, LangDetectException
from deep_translator import GoogleTranslator

dotenv.load_dotenv()

# ----- Configuración -----

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o-mini"
DB_FILE = Path("incidents.json")
LANG_SISTEMA = "es"

LANG_NOMBRES = {
    "es": "Español",
    "en": "Inglés",
    "fr": "Francés",
    "de": "Alemán",
    "pt": "Portugués",
    "it": "Italiano",
    "zh": "Chino",
    "ja": "Japonés",
    "ar": "Árabe",
    "ru": "Ruso",
    "ko": "Coreano",
    "nl": "Holandés",
    "pl": "Polaco",
    "tr": "Turco",
    "hi": "Hindi",
}

client = openai.OpenAI(api_key=API_KEY)

# ----- Persistencia -----


def cargar_incidentes():

    if DB_FILE.exists():
        return json.loads(DB_FILE.read_text(encoding="utf-8"))

    return []


def guardar_incidentes(incidentes):

    DB_FILE.write_text(
        json.dumps(
            incidentes,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8",
    )

# ----- Idioma / Traducción -----


def detectar_idioma(texto):

    try:
        return detect(texto)

    except LangDetectException:
        return "desconocido"


def traducir_a_espanol(texto, idioma_origen):

    if idioma_origen == LANG_SISTEMA:
        return texto

    try:
        return GoogleTranslator(
            source=idioma_origen,
            target=LANG_SISTEMA
        ).translate(texto)

    except Exception as e:
        print(e)
        return texto


def traducir_a_idioma(texto, idioma_destino):

    try:
        return GoogleTranslator(
            source=LANG_SISTEMA,
            target=idioma_destino
        ).translate(texto)

    except Exception as e:
        return f"[Error de traducción: {e}]"

# ----- OpenAI -----


def analizar_incidente(texto_es):

    prompt = """
Eres un sistema de gestión de incidentes corporativos.

El texto ya está en español.

Responde únicamente JSON válido:

{
    "categoria":"<Técnico | Seguridad | Operacional | RR.HH. | Infraestructura | Otro>",
    "severidad":"<baja | media | alta | critica>",
    "resumen":"<máximo 30 palabras>"
}
""".strip()

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": texto_es
            },
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    return json.loads(
        response.choices[0].message.content.strip()
    )

# ----- NUEVA función reutilizable -----


def procesar_incidente(texto):

    if not texto.strip():
        raise ValueError("Texto vacío")

    codigo_idioma = detectar_idioma(texto)

    nombre_idioma = LANG_NOMBRES.get(
        codigo_idioma,
        codigo_idioma.upper()
    )

    if codigo_idioma != LANG_SISTEMA:
        texto_es = traducir_a_espanol(
            texto,
            codigo_idioma
        )
    else:
        texto_es = texto

    analisis = analizar_incidente(texto_es)

    incidente = {
        "id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now().isoformat(
            timespec="seconds"
        ),
        "texto_original": texto,
        "idioma_codigo": codigo_idioma,
        "idioma_nombre": nombre_idioma,
        "texto_es": texto_es,
        "categoria": analisis["categoria"],
        "severidad": analisis["severidad"],
        "resumen": analisis["resumen"],
    }

    incidentes = cargar_incidentes()
    incidentes.append(incidente)
    guardar_incidentes(incidentes)

    return incidente

# ----- CLI original -----


def registrar_incidente():

    print("\n" + "═" * 60)
    print(" NUEVO REPORTE")
    print("═" * 60)

    texto = input("> ").strip()

    try:

        incidente = procesar_incidente(texto)

        print("\nGuardado correctamente")
        print(f"ID: {incidente['id']}")
        print(f"Categoria: {incidente['categoria']}")
        print(f"Severidad: {incidente['severidad']}")
        print(f"Resumen: {incidente['resumen']}")

    except Exception as e:
        print(e)


def listar_incidentes():

    incidentes = cargar_incidentes()

    if not incidentes:
        print("\nNo hay incidentes.")
        return

    print("\n" + "═" * 60)

    for inc in incidentes:

        print(f"\n[{inc['id']}]")

        print(
            f"{inc['timestamp']} | "
            f"{inc['categoria']} | "
            f"{inc['severidad']}"
        )

        print(inc["resumen"])


def menu():

    opciones = {
        "1": (
            "Registrar incidente",
            registrar_incidente
        ),
        "2": (
            "Ver incidentes",
            listar_incidentes
        ),
        "3": (
            "Salir",
            None
        ),
    }

    while True:

        print("\n===== MENU =====")

        for k, (desc, _) in opciones.items():
            print(f"[{k}] {desc}")

        eleccion = input("Opción: ").strip()

        if eleccion == "3":
            break

        elif eleccion in opciones:
            opciones[eleccion][1]()

        else:
            print("Opción inválida")


if __name__ == "__main__":
    menu()