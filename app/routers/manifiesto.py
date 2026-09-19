"""Endpoints de manifiesto — MS4-02 + MS4-03 + MS4-04 implementados."""
from fastapi import APIRouter, HTTPException, status

from app.services.manifiesto import (
    VueloNoExiste,
    obtener_manifiesto,
    obtener_pasajeros,
    obtener_resumen,
)

router = APIRouter(prefix="/api/manifiesto", tags=["manifiesto"])


# --- Ejemplos para OpenAPI/Swagger ---

_EJEMPLO_MANIFIESTO = {
    "vuelo_id": 6058,
    "vuelo": {
        "id": 6058, "numero": "LA0032",
        "hora_programada": "2026-08-17T21:55:00Z",
        "hora_real": "2026-08-17T22:11:00Z",
        "estado": "Aterrizado", "tipo": "Internacional",
        "origen": "LIM", "destino": "SCL",
        "aeronave": {"placa": "OB-1111", "modelo": "Boeing 787-9", "clase": "E"},
        "aerolinea": {"ruc": "20100000018", "nombre": "GOL", "alianza": "Ninguna"},
    },
    "pasajeros": [
        {
            "id_ticket": 1, "id_persona": 134482, "estado_boarding": "Embarcado",
            "equipaje": [{"id": "BHS0000000001", "peso": "17.65"}],
        }
    ],
    "tripulacion": [{"id_empleado": 1542, "nombre": "Carlos", "num_licencia": "DGAC-001542"}],
    "incidencias_abiertas": [
        {"id": 1, "gravedad": "Alta", "tipo_incidencia": "Falta_Combustible", "fecha_cierre": None}
    ],
    "warnings": [],
}

_EJEMPLO_MANIFIESTO_DEGRADED = {
    **_EJEMPLO_MANIFIESTO,
    "incidencias_abiertas": [],
    "warnings": ["MS3/incidencias: MS3 inalcanzable — connection error"],
}

_EJEMPLO_RESUMEN = {
    "vuelo_id": 6058,
    "pasajeros_total": 2,
    "equipaje_kg_total": 38.25,
    "incidencias_abiertas": 1,
    "warnings": [],
}

_EJEMPLO_404 = {"detail": "Vuelo 99999 no encontrado en MS2"}


@router.get(
    "/{vuelo_id}",
    summary="Manifiesto consolidado del vuelo",
    description=(
        "Agrega vuelo + aeronave + aerolínea (MS2), pasajeros con ticket / "
        "checkin / equipaje (MS1), tripulación asignada (MS2) y recursos + "
        "incidencias abiertas (MS3). Si alguna dependencia no responde, el "
        "campo correspondiente queda vacío y se agrega un mensaje a `warnings[]` "
        "(MS4-04, respuesta parcial)."
    ),
    responses={
        200: {
            "description": "Manifiesto — completo o parcial con warnings[]",
            "content": {
                "application/json": {
                    "examples": {
                        "completo": {
                            "summary": "Todas las dependencias responden",
                            "value": _EJEMPLO_MANIFIESTO,
                        },
                        "con_warning": {
                            "summary": "Una dependencia caída → 200 con warnings[]",
                            "value": _EJEMPLO_MANIFIESTO_DEGRADED,
                        },
                    }
                }
            },
        },
        404: {
            "description": "Vuelo no existe en MS2",
            "content": {"application/json": {"example": _EJEMPLO_404}},
        },
    },
)
async def manifiesto(vuelo_id: int) -> dict:
    try:
        return await obtener_manifiesto(vuelo_id)
    except VueloNoExiste as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get(
    "/{vuelo_id}/pasajeros",
    summary="Pasajeros del vuelo con ticket + checkin + equipaje",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "vuelo_id": 6058,
                        "total": 2,
                        "pasajeros": _EJEMPLO_MANIFIESTO["pasajeros"],
                    }
                }
            }
        },
        404: {"content": {"application/json": {"example": _EJEMPLO_404}}},
    },
)
async def pasajeros(vuelo_id: int) -> dict:
    try:
        return await obtener_pasajeros(vuelo_id)
    except VueloNoExiste as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get(
    "/{vuelo_id}/resumen",
    summary="Conteos: pax, kg equipaje total, incidencias abiertas",
    responses={
        200: {"content": {"application/json": {"example": _EJEMPLO_RESUMEN}}},
        404: {"content": {"application/json": {"example": _EJEMPLO_404}}},
    },
)
async def resumen(vuelo_id: int) -> dict:
    try:
        return await obtener_resumen(vuelo_id)
    except VueloNoExiste as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
