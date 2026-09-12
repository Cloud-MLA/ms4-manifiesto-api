"""Cliente de MS3 — Infraestructura / Incidencias."""
from typing import Any

from app.clients.base import HttpClient
from app.config import settings

_client = HttpClient(
    base_url=settings.ms3_base_url,
    timeout_seconds=settings.http_timeout_seconds,
    retries=settings.http_retries,
    service_name="MS3",
)


class MS3Client:
    """Métodos que MS4 usa contra MS3."""

    async def get_asignaciones_de_vuelo(self, vuelo_id: int) -> list[dict[str, Any]]:
        """`GET /infra/asignaciones?vuelo_id={id}` — recursos asignados al vuelo."""
        response = await _client.get(f"/api/infra/asignaciones?vuelo_id={vuelo_id}")
        response.raise_for_status()
        return response.json()

    async def get_incidencias_abiertas_de_vuelo(self, vuelo_id: int) -> list[dict[str, Any]]:
        """`GET /infra/incidencias?vuelo_id={id}&abierta=true` — incidencias sin
        `fecha_cierre` que retrasan/afectan el vuelo.
        """
        response = await _client.get(f"/api/infra/incidencias?vuelo_id={vuelo_id}&abierta=true")
        response.raise_for_status()
        return response.json()

    async def health_check(self) -> dict[str, Any]:
        return await _client.health_check()


ms3_client = MS3Client()
