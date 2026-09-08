"""Endpoints de manifiesto — stubs.

La implementación real llega en MS4-02 (F1 del plan) cuando MS2 tenga
`GET /vuelos/{id}/exists` y MS1/MS3 sus endpoints listados en requerimientos §4.
"""
from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/manifiesto", tags=["manifiesto"])


_STUB_MSG = "MS4-02 pendiente — llegara en F1 cuando MS1/MS2/MS3 expongan sus endpoints"


@router.get(
    "/{vuelo_id}",
    summary="Manifiesto consolidado del vuelo",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def manifiesto(vuelo_id: int) -> dict:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={"tarea": "MS4-02", "vuelo_id": vuelo_id, "mensaje": _STUB_MSG},
    )


@router.get(
    "/{vuelo_id}/pasajeros",
    summary="Pasajeros del vuelo con ticket + checkin + equipaje",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def pasajeros(vuelo_id: int) -> dict:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={"tarea": "MS4-03", "vuelo_id": vuelo_id, "mensaje": _STUB_MSG},
    )


@router.get(
    "/{vuelo_id}/resumen",
    summary="Conteos: pax, kg equipaje total, incidencias abiertas",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def resumen(vuelo_id: int) -> dict:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={"tarea": "MS4-03", "vuelo_id": vuelo_id, "mensaje": _STUB_MSG},
    )
