"""Cliente de MS1 — Pasajeros / Tickets."""
from typing import Any

from app.clients.base import HttpClient
from app.config import settings

_client = HttpClient(
    base_url=settings.ms1_base_url,
    timeout_seconds=settings.http_timeout_seconds,
    retries=settings.http_retries,
    service_name="MS1",
)


class MS1Client:
    """Métodos que MS4 usa contra MS1."""

    async def get_tickets_de_vuelo(self, vuelo_id: int) -> list[dict[str, Any]]:
        """`GET /pasajeros/tickets?vuelo_id={id}` — todos los tickets del vuelo,
        con pasajero + checkin + equipaje embebidos si el endpoint los devuelve.
        """
        response = await _client.get(f"/api/pasajeros/tickets?vuelo_id={vuelo_id}")
        response.raise_for_status()
        return response.json()

    async def health_check(self) -> dict[str, Any]:
        return await _client.health_check()


ms1_client = MS1Client()
