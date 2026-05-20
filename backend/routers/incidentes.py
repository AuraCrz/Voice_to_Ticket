'''
routers/incidentes.py
Endpoints para registro, consulta y estadísticas de incidentes.
'''

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from typing import Optional

from models.schemas import (
    IncidenteTextRequest,
    IncidenteResponse,
    StatsResponse,
)
from services.llm        import analizar_incidente
from services.traduccion import detectar_idioma, traducir_a_espanol
from services.voz        import transcribir_audio
from config              import LANG_NOMBRES, load_config

router  = APIRouter(prefix="/incidentes", tags=["Incidentes"])
BASE_DIR = Path(__file__).parent.parent 
DB_FILE  = BASE_DIR / "data" / "incidents.json"

# ----- Persistencia local -----

def _cargar() -> list[dict]:
    if DB_FILE.exists():
        return json.loads(DB_FILE.read_text(encoding="utf-8"))
    return []


def _guardar(incidentes: list[dict]) -> None:
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    DB_FILE.write_text(
        json.dumps(incidentes, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ----- Pipeline compartido -----

def _procesar_y_guardar(texto: str, fuente: str, voz_meta: dict | None = None) -> dict:
    '''
    Pipeline común para texto escrito y voz:
    detectar idioma → traducir → analizar → guardar → retornar incidente.
    '''
    settings      = load_config()
    idioma_codigo = settings.get("idioma_iso", "es") if fuente == "voz" else detectar_idioma(texto)
    idioma_nombre = LANG_NOMBRES.get(idioma_codigo, idioma_codigo.upper())

    texto_es = traducir_a_espanol(texto, idioma_codigo)
    analisis = analizar_incidente(texto_es)

    incidente = {
        "id"            : str(uuid.uuid4())[:8],
        "timestamp"     : datetime.now().isoformat(timespec="seconds"),
        "fuente"        : fuente,
        "texto_original": texto,
        "voz_duracion"  : voz_meta.get("duracion") if voz_meta else None,
        "voz_status"    : voz_meta.get("status")   if voz_meta else None,
        "idioma_codigo" : idioma_codigo,
        "idioma_nombre" : idioma_nombre,
        "texto_es"      : texto_es,
        "categoria"     : analisis["categoria"],
        "severidad"     : analisis["severidad"],
        "resumen"       : analisis["resumen"],
    }

    incidentes = _cargar()
    incidentes.append(incidente)
    _guardar(incidentes)

    return incidente


# ----- Endpoints -----

@router.get("/stats", response_model=StatsResponse)
def obtener_stats():
    '''Métricas para el Dashboard: total, resueltos, actividad semanal.'''
    incidentes  = _cargar()
    total       = len(incidentes)
    resueltos   = sum(1 for i in incidentes if i.get("severidad") == "baja")
    hace_semana = datetime.now() - timedelta(days=7)
    esta_semana = sum(
        1 for i in incidentes
        if datetime.fromisoformat(i["timestamp"]) >= hace_semana
    )
    porcentaje = round((esta_semana / total * 100), 1) if total else 0.0

    return StatsResponse(
        total             = total,
        resueltos         = resueltos,
        esta_semana       = esta_semana,
        porcentaje_semana = porcentaje,
    )


@router.get("", response_model=list[IncidenteResponse])
def listar_incidentes(
    severidad : Optional[str] = Query(None),
    categoria : Optional[str] = Query(None),
):
    '''Lista todos los incidentes. Acepta filtros opcionales por severidad y categoría.'''
    incidentes = _cargar()

    if severidad:
        incidentes = [i for i in incidentes if i.get("severidad") == severidad]
    if categoria:
        incidentes = [i for i in incidentes if i.get("categoria") == categoria]

    return incidentes


@router.get("/{incidente_id}", response_model=IncidenteResponse)
def obtener_incidente(incidente_id: str):
    '''Retorna el detalle de un incidente por su ID.'''
    incidentes = _cargar()
    for inc in incidentes:
        if inc["id"] == incidente_id:
            return inc
    raise HTTPException(status_code=404, detail="Incidente no encontrado.")


@router.post("", response_model=IncidenteResponse, status_code=201)
def registrar_por_texto(body: IncidenteTextRequest):
    '''Registra un incidente a partir de texto escrito.'''
    if not body.texto.strip():
        raise HTTPException(status_code=422, detail="El texto no puede estar vacío.")
    return _procesar_y_guardar(body.texto.strip(), fuente="teclado")


@router.post("/voz", response_model=IncidenteResponse, status_code=201)
async def registrar_por_voz(audio: UploadFile = File(...)):
    '''
    Registra un incidente a partir de un archivo de audio.
    El frontend envía el audio grabado desde el navegador (webm/mp4/wav).
    '''
    settings    = load_config()
    idioma_iso  = settings.get("idioma_iso", "es")
    audio_bytes = await audio.read()

    resultado = await transcribir_audio(audio_bytes, idioma_iso)

    if resultado["status"] != "success" or not resultado["texto"]:
        raise HTTPException(
            status_code=422,
            detail=f"No se pudo transcribir el audio: {resultado.get('error', 'audio no reconocido')}",
        )

    voz_meta = {"status": resultado["status"], "duracion": None}
    return _procesar_y_guardar(resultado["texto"], fuente="voz", voz_meta=voz_meta)