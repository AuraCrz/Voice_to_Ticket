# Frontend - Voice to Ticket AI

Interfaz web en React + Vite para el proyecto Voice to Ticket AI.

## Requisitos

- Node.js instalado
- npm instalado
- Backend Python configurado si quieres usar el flujo completo del proyecto

## Instalacion

Desde esta carpeta:

```powershell
cd "C:\...\ticket voice\Voice_to_Ticket\Voice_to_Ticket\Frontend"
npm install
```

## Ejecutar el frontend

```powershell
npm run dev
```

Vite mostrara una URL local parecida a:

```text
http://localhost:5173/
```

Abre esa URL en el navegador para ver la app.

## Ejecutar backend y frontend juntos

Abre dos terminales.

Terminal 1 - backend:

```powershell
cd "C:\...\ticket voice\Voice_to_Ticket\Voice_to_Ticket"
$env:API_KEY="tu_api_key_de_openai"
pip install -r Backend\requirements.txt
python Backend\voicetoticket.py
```

Terminal 2 - frontend:

```powershell
cd "C:\...\ticket voice\Voice_to_Ticket\Voice_to_Ticket\Frontend"
npm install
npm run dev
```

Nota: el backend actual funciona como aplicacion de consola interactiva. Todavia no expone una API HTTP para que el frontend se comunique directamente con el.

## Scripts disponibles

```powershell
npm run dev
```

Inicia el servidor de desarrollo.

```powershell
npm run build
```

Genera la version de produccion en la carpeta `dist`.

```powershell
npm run preview
```

Sirve localmente la version generada con `npm run build`.

```powershell
npm run lint
```

Ejecuta ESLint sobre el codigo del frontend.

## Estructura principal

```text
Frontend/
+-- public/
+-- src/
|   +-- assets/
|   +-- components/
|   +-- pages/
|   +-- App.jsx
|   +-- App.css
|   +-- index.css
|   +-- main.jsx
+-- index.html
+-- package.json
+-- vite.config.js
```
