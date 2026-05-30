# Voice to Ticket 🎫

Sistema multilingüe de reporte de incidentes que detecta automáticamente el idioma del texto, lo normaliza al español y lo procesa con IA para generar tickets estructurados dentro de un sistema empresarial.

## ¿Qué hace?

- Recibe incidencias en cualquier idioma (Español, Inglés, Alemán, Francés, entre otros)
- Detecta el idioma automáticamente sin consumir tokens
- Traduce al español como idioma base del sistema
- Clasifica la incidencia por **categoría** y **severidad** usando un LLM
- Genera un resumen estructurado listo para convertirse en ticket
- Guarda los reportes localmente en un archivo JSON

## Instalación

```bash
git clone https://github.com/Voice_to_Ticket
cd "nombre_carpeta_clonada"
pip install -r requirements.txt
```

## Configuración
La API Key de OpenAI **nunca** se escribe directamente en el código. Guárdala como variable de entorno:

```bash
# Linux / macOS
export OPENAI_API_KEY="sk-..."

# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-..."
```

## Uso

```bash
python voicetoticket.py
```

Opciones disponibles en el menú:
1. Registrar nuevo incidente
2. Ver incidentes registrados
3. Salir

## Estructura del proyecto

```
voice-to-ticket/
├── incident_reporter.py   # Script principal
├── incidents.json         # Base de datos local (se crea automáticamente)
├── requirements.txt       # Dependencias
└── README.md
```

## Decisiones de diseño del MVP

- El LLM **solo recibe texto en español**, lo que reduce el consumo de tokens en ~60-70% respecto a dejarle también la traducción.
- La detección y traducción corren con librerías gratuitas, por lo que el costo de la API de OpenAI aplica únicamente al análisis semántico.
- La persistencia en JSON es intencional para el MVP; la arquitectura objetivo usa AWS RDS.

## Arquitectura objetivo

El MVP es la primera iteración de un sistema más amplio que incluirá:

- **Frontend** Vue con soporte de voz y texto
- **Backend** Flask / AWS API Gateway
- **Speech-to-Text** con AWS Transcribe
- **Confidence Validator** para decidir si un reporte tiene suficiente información antes de crear el ticket
- **Otobo Ticketing System** como destino final de los reportes
- **AWS RDS** para persistencia y **AWS SQS** para manejo de cola de incidentes
