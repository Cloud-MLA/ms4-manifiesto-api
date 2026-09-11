"""Cliente de MS2 — Vuelos / Operaciones."""
from typing import Any

import httpx

from app.clients.base import HttpClient
from app.config import settings

_client = HttpClient(
    base_url=settings.ms2_base_url,
    timeout_seconds=settings.http_timeout_seconds,
    retries=settings.http_retries,
    service_name="MS2",
)


class MS2Client:
    """Métodos que MS4 usa contra MS2."""

    async def vuelo_exists(self, vuelo_id: int) -> bool:
        """`GET /vuelos/{id}/exists` — endpoint liviano para chequear si el vuelo
        existe antes de gastar llamadas más pesadas.

        Acepta dos convenciones habituales:
        - MS2 devuelve 404 cuando no existe.
        - MS2 devuelve 200 con body `{"exists": false}` cuando no existe.
        """
        try:
            response = await _client.get(f"/api/vuelos/{vuelo_id}/exists")
        except httpx.HTTPError:
            return False
        if response.status_code != 200:
            return False
        try:
            body = response.json()
        except ValueError:
            return True  # 200 sin body válido → asumimos que existe
        return bool(body.get("exists", True))

    async def get_vuelo_completo(self, vuelo_id: int) -> dict[str, Any]:
        """`GET /vuelos/{id}` — datos del vuelo con aeronave y aerolínea embebidas."""
        response = await _client.get(f"/api/vuelos/{vuelo_id}")
        response.raise_for_status()
        return response.json()

    async def get_tripulacion_de_vuelo(self, vuelo_id: int) -> list[dict[str, Any]]:
        """`GET /vuelos/{id}/tripulacion` — lista de tripulantes asignados."""
        response = await _client.get(f"/api/vuelos/{vuelo_id}/tripulacion")
        response.raise_for_status()
        return response.json()

    async def health_check(self) -> dict[str, Any]:
        return await _client.health_check()


ms2_client = MS2Client()
