"""Endpoints de manifiesto — MS4-02 + MS4-03 + MS4-04 implementados."""
from fastapi import APIRouter, HTTPException, status

from app.services.manifiesto import (
    VueloNoExiste,
    obtener_manifiesto,
    obtener_pasajeros,
    obtener_resumen,
)

router = APIRouter(prefix="/api/manifiesto", tags=["manifiesto"])


@router.get(
    "/{vuelo_id}",
    summary="Manifiesto consolidado del vuelo",
    description=(
        "Agrega vuelo + aeronave + aerolínea (MS2), pasajeros con ticket / "
        "checkin / equipaje (MS1), tripulación asignada (MS2) y recursos + "
        "incidencias abiertas (MS3). Si alguna dependencia no responde, el "
        "campo correspondiente queda vacío y se agrega un mensaje a `warnings[]`."
    ),
)
async def manifiesto(vuelo_id: int) -> dict:
    try:
        return await obtener_manifiesto(vuelo_id)
    except VueloNoExiste as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get(
    "/{vuelo_id}/pasajeros",
    summary="Pasajeros del vuelo con ticket + checkin + equipaje",
)
async def pasajeros(vuelo_id: int) -> dict:
    try:
        return await obtener_pasajeros(vuelo_id)
    except VueloNoExiste as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get(
    "/{vuelo_id}/resumen",
    summary="Conteos: pax, kg equipaje total, incidencias abiertas",
)
async def resumen(vuelo_id: int) -> dict:
    try:
        return await obtener_resumen(vuelo_id)
    except VueloNoExiste as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
