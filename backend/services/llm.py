'''
services/llm.py
Análisis de incidentes usando OpenAI GPT.
'''

import json
import os
import openai
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("API_KEY"))
MODEL  = "gpt-4o-mini"


def analizar_incidente(texto_es: str) -> dict:
    '''
    Recibe texto en español y retorna dict con:
    - categoria : Técnico | Seguridad | Operacional | RR.HH. | Infraestructura | Otro
    - severidad : baja | media | alta | critica
    - resumen   : máximo 30 palabras
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
