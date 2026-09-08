"""Health checks del servicio y de sus dependencias."""
import asyncio

from fastapi import APIRouter

from app.clients.ms1 import ms1_client
from app.clients.ms2 import ms2_client
from app.clients.ms3 import ms3_client

router = APIRouter(tags=["health"])


@router.get("/health", summary="Estado propio del servicio")
async def health() -> dict[str, str]:
    return {"status": "up", "service": "ms4-manifiesto-api"}


@router.get(
    "/health/dependencias",
    summary="Estado de MS1, MS2 y MS3",
    description=(
        "Consulta el `/health` de cada dependencia en paralelo. "
        "Devuelve `up`/`degraded`/`down` por servicio. "
        "`overall` es `up` si los 3 están `up`, `degraded` si al menos uno responde "
        "pero no todos, o `down` si ninguno responde."
    ),
)
async def dependencias() -> dict:
    ms1, ms2, ms3 = await asyncio.gather(
        ms1_client.health_check(),
        ms2_client.health_check(),
        ms3_client.health_check(),
    )
    estados = {"ms1": ms1, "ms2": ms2, "ms3": ms3}
    ups = sum(1 for s in estados.values() if s["status"] == "up")
    if ups == 3:
        overall = "up"
    elif ups == 0:
        overall = "down"
    else:
        overall = "degraded"
    return {"overall": overall, "dependencias": estados}
