# Voice to Ticket 🎫

Sistema multilingüe de reporte de incidentes que detecta automáticamente el idioma del texto, lo normaliza al español y lo procesa con IA para generar tickets estructurados dentro de un sistema empresarial.

## Evolución del proyecto: Integración Fullstack
Inicialmente el sistema funcionaba con una interfaz de linea de comandos, actualmente el sistema ha migrado a una arquitectura **cliente-servidor**. Durante este proceso de conexión del frontend y el backend, se realizaron las siguientes implementaciones:

* **Migración a API RESTful:** Se transformó el script iterativo tradicional de Python en un servidor web activo mediante **Flask**, exponiendo endpoints estructurados (`/api/incidentes`, `/api/login`, `/api/register`).
* **Implementación y Control de CORS:** Se integró la extensión `flask-cors` dentro del backend. Esto solucionó los bloqueos de seguridad del navegador por peticiones *preflight* (`OPTIONS 404`) derivados de la comunicación cruzada entre los entornos locales (puerto `5173` de Vite y puerto `5000` de Flask).
* **Módulo de Autenticación Local Expreso:** Para la validación de usuarios se diseñó un sistema de persistencia de usuarios basado en un archivo local (`users.json`).

---


## ¿Qué hace?

- Recibe incidencias en cualquier idioma (Español, Inglés, Alemán, Francés, entre otros)
- Detecta el idioma automáticamente sin consumir tokens
- Traduce al español como idioma base del sistema
- Clasifica la incidencia por **categoría** y **severidad** usando un LLM
- Genera un resumen estructurado listo para convertirse en ticket
- Guarda los reportes localmente en un archivo JSON
- Almacena tanto de reportes (`incidents.json`) como de credenciales (`users.json`).

## Estructura 
Estructura Actual del Proyecto

```text
Voice_to_Ticket/
├── incidents.json         # Base de datos local de reportes (Generada en la raíz)
├── README.md              # Documentación del proyecto
├── Backend/
│   ├── voicetoticket.py   # Servidor Flask, endpoints API y lógica de IA
│   ├── users.json         # Base de datos local de usuarios (Auto-generada)
│   ├── requirements.txt   # Dependencias de Python (Flask, OpenAI, CORS, etc.)
│   ├── .env               # Variables de entorno (Claves de API de OpenAI)
│   └── .venv/             # Entorno virtual de Python
└── Frontend/
    ├── index.html
    ├── package-lock.json
    ├── package.json       # Dependencias del ecosistema Node/React
    ├── vite.config.js     # Configuración del empaquetador Vite
    ├── eslint.config.js
    ├── dist/              # Compilación de producción de la app
    ├── node_modules/      # Módulos instalados de Node.js
    ├── public/            # Recursos estáticos públicos
    └── src/               # Código fuente de React
        ├── App.css        # Estilos generales de la aplicación
        ├── App.jsx        # Enrutador y controlador de vistas principal
        ├── index.css      # Configuraciones base de Tailwind CSS
        ├── main.jsx       # Punto de entrada de la aplicación React
        ├── api.js         # Configuración centralizada de peticiones HTTP
        ├── assets/        # Recursos visuales e imágenes locales
        ├── components/    # Componentes modulares de la interfaz
        │   ├── Header.jsx    # Barra superior de navegación del sistema
        │   ├── Login.jsx     # Interfaz de autenticación y registro asíncrono
        │   ├── Sidebar.jsx   # Menú lateral de navegación del Dashboard
        │   └── StatsCard.jsx # Tarjetas de métricas e indicadores clave
        └── pages/         # Contenedores de las vistas principales
        ```

## Instalación

```bash
git clone https://github.com/AuraCrz/Voice_to_Ticket
cd "nombre_carpeta_clonada"
```

## Configuración
La API Key de OpenAI **nunca** se escribe directamente en el código. Guárdala como variable de entorno:

```bash
# Linux / macOS
export OPENAI_API_KEY="sk-..."

# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-..."
```

## Back-end
```bash
cd backend
pip install -r requirements.txt
python voicetoticket.py
```
El servidor backend se inicializará escuchando en la dirección: http://localhost:5000

## Front-end
En una nueva terminal 
```bash
cd frontend
npm install
npm run dev
```
Accede a la aplicación web a través de la dirección local provista por Vite (típicamente http://localhost:5173)


## Decisiones de diseño del MVP

- El LLM **solo recibe texto en español**, lo que reduce el consumo de tokens en ~60-70% respecto a dejarle también la traducción.
- La detección y traducción corren con librerías gratuitas, por lo que el costo de la API de OpenAI aplica únicamente al análisis semántico.
- La persistencia en JSON es intencional para el MVP; la arquitectura objetivo usa AWS RDS.

## Arquitectura objetivo

El MVP es la primera iteración de un sistema más amplio que incluirá:

- **Frontend** React con soporte de voz y texto
- **Backend** Flask / AWS API Gateway
- **Speech-to-Text** con AWS Transcribe
- **Confidence Validator** para decidir si un reporte tiene suficiente información antes de crear el ticket
- **Otobo Ticketing System** como destino final de los reportes
- **AWS RDS** para persistencia y **AWS SQS** para manejo de cola de incidentes
