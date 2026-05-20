import json
import uuid
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS

import openai, os # LLM
import dotenv      # Carga variables de entorno desde .env

dotenv.load_dotenv()

app = Flask(__name__)
CORS(app)  # Esto le da permiso al Frontend de Vite para conectarse

# Dependencias gratuitas para idioma y traducción
from langdetect import detect, LangDetectException
from deep_translator import GoogleTranslator


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
def registrar_incidente():
    print("\n" + "═" * 60)
    print("  NUEVO REPORTE DE INCIDENTE")
    print("═" * 60)
    texto = input("Describe el incidente (en cualquier idioma):\n> ").strip()

    if not texto:
        print("[!] No ingresaste texto. Cancelado.")
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

    # Traducción adicional opcional
    opcion = input("\n¿Deseas ver el resumen en otro idioma? (s/no): ").strip().lower()
    if opcion in ("s", "si", "sí", "y", "yes"):
        idioma_extra = input(
            "Código de idioma destino (ej. en=inglés, fr=francés, de=alemán): "
        ).strip().lower()
        traduccion_extra = traducir_a_idioma(analisis["resumen"], idioma_extra)
        print(f"  → {traduccion_extra}")

    # Guardar
    guardar = input("\n¿Guardar este reporte? (s/no): ").strip().lower()
    if guardar in ("s", "si", "sí", "y", "yes"):
        incidente = {
            "id"             : str(uuid.uuid4())[:8],
            "timestamp"      : datetime.now().isoformat(timespec="seconds"),
            "texto_original" : texto,
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
        "1": ("Registrar nuevo incidente",  registrar_incidente),
        "2": ("Ver incidentes registrados", listar_incidentes),
        "3": ("Salir",                      None),
    }

    while True:
        print()
        for k, (desc, _) in opciones.items():
            print(f"  [{k}] {desc}")
        eleccion = input("\n  Opción: ").strip()

        if eleccion == "3":
            print("\n  Hasta luego.\n")
            break
        elif eleccion in opciones:
            opciones[eleccion][1]()
        else:
            print("  Opción no válida.")
            
# ----- Configuración y Persistencia de Usuarios -----
USERS_FILE = Path("users.json")

def cargar_usuarios() -> list[dict]:
    if USERS_FILE.exists():
        return json.loads(USERS_FILE.read_text(encoding="utf-8"))
    return []

def guardar_usuarios(usuarios: list[dict]) -> None:
    USERS_FILE.write_text(
        json.dumps(usuarios, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

# ----- Endpoints de Autenticación para el Frontend -----

@app.route('/api/register', methods=['POST'])
def api_registrar_usuario():
    """
    Registra un usuario nuevo desde la interfaz y lo guarda en users.json
    """
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not email or not password:
            return jsonify({"error": "Correo y contraseña son obligatorios."}), 400

        usuarios = cargar_usuarios()

        # Verificar si el correo ya existe
        if any(u['email'] == email for u in usuarios):
            return jsonify({"error": "El correo electrónico ya está registrado."}), 400

        # Crear y guardar el nuevo usuario
        nuevo_usuario = {
            "id": str(uuid.uuid4())[:8],
            "email": email,
            "password": password  # En producción usa hashing (ej. bcrypt), para entorno local sirve así
        }
        
        usuarios.append(nuevo_usuario)
        guardar_usuarios(usuarios)

        return jsonify({"message": "Usuario registrado con éxito.", "user": {"email": email}}), 201

    except Exception as e:
        return jsonify({"error": f"Error en el registro: {str(e)}"}), 500


@app.route('/api/login', methods=['POST'])
def api_login_usuario():
    """
    Valida las credenciales del usuario contra el archivo users.json
    """
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        usuarios = cargar_usuarios()

        # Buscar si coinciden correo y contraseña
        usuario_valido = next((u for u in usuarios if u['email'] == email and u['password'] == password), None)

        if not usuario_valido:
            return jsonify({"error": "Correo o contraseña incorrectos."}), 401

        # Retornamos éxito y un token ficticio para que React te dé acceso al Dashboard
        return jsonify({
            "message": "Inicio de sesión exitoso.",
            "token": "token-ficticio-asociado-ia",
            "user": {"email": email}
        }), 200

    except Exception as e:
        return jsonify({"error": f"Error en el inicio de sesión: {str(e)}"}), 500            

#endpoints para la conexion con el frontend

@app.route('/api/incidentes', methods=['POST'])
def api_registrar_incidente():
    """
    Recibe el texto del incidente enviado desde el frontend en formato JSON,
    lo procesa con la IA, lo guarda en el archivo local y retorna el resultado.
    """
    try:
        data = request.get_json()
        
        # Validar que el frontend envíe el campo 'texto'
        if not data or 'texto' not in data or not data['texto'].strip():
            return jsonify({"error": "No se proporcionó la descripción del incidente."}), 400
        
        texto = data['texto'].strip()

        # 1. Detección de idioma
        codigo_idioma = detectar_idioma(texto)
        nombre_idioma = LANG_NOMBRES.get(codigo_idioma, codigo_idioma.upper())

        # 2. Traducción a español si es necesario
        if codigo_idioma != LANG_SISTEMA:
            texto_es = traducir_a_espanol(texto, codigo_idioma)
        else:
            texto_es = texto

        # 3. Análisis inteligente con GPT-4o-mini
        analisis = analizar_incidente(texto_es)

        # 4. Estructurar el objeto del incidente
        nuevo_incidente = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "texto_original": texto,
            "idioma_codigo": codigo_idioma,
            "idioma_nombre": nombre_idioma,
            "texto_es": texto_es,
            "categoria": analisis.get("categoria", "Otro"),
            "severidad": analisis.get("severidad", "baja"),
            "resumen": analisis.get("resumen", "")
        }

        # 5. Persistencia en el JSON (incidents.json)
        incidentes = cargar_incidentes()
        incidentes.append(nuevo_incidente)
        guardar_incidentes(incidentes)  

        # Retornamos el incidente creado para que el Frontend lo muestre de inmediato
        return jsonify({
            "message": "Incidente registrado con éxito",
            "incidente": nuevo_incidente
        }), 201

    except Exception as e:
        return jsonify({"error": f"Error interno en el servidor: {str(e)}"}), 500


@app.route('/api/incidentes', methods=['GET'])
def api_listar_incidentes():
    """
    Retorna la lista completa de todos los incidentes guardados para
    que el Dashboard de Berenice pueda pintarlos en una tabla o gráficas.
    """
    try:
        incidentes = cargar_incidentes()
        return jsonify(incidentes), 200
    except Exception as e:
        return jsonify({"error": f"No se pudieron cargar los datos: {str(e)}"}), 500

if __name__ == "__main__":
    #menu()
    # Cambiamos menu() por app.run para arrancar el servidor de la API
    print("Iniciando Servidor Flask en http://localhost:5000 ...")
    app.run(port=5000, debug=True)