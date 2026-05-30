from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from incident_service import (
    procesar_incidente,
    cargar_incidentes,
)

# ----- FastAPI -----

app = FastAPI(
    title="VoiceTicket API",
    description="API para gestión inteligente de incidentes",
    version="1.0.0"
)

# ----- CORS -----

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Modelo Request -----


class IncidentRequest(BaseModel):
    texto: str


# ----- Health Check -----


@app.get("/")
def root():

    return {
        "message": "VoiceTicket API funcionando"
    }


# ----- Crear incidente -----


@app.post("/incidents")
def create_incident(data: IncidentRequest):

    try:

        incidente = procesar_incidente(
            data.texto
        )

        return incidente

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Error interno: {str(e)}"
        )


# ----- Listar incidentes -----


@app.get("/incidents")
def get_incidents():

    try:

        return cargar_incidentes()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )