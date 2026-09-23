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
    """Métodos que MS4 usa contra MS1.

    Nota de despliegue: MS1 real (Guillermo, FastAPI) monta los routers en la
    raíz (`/tickets`, `/pasajeros`, `/categorias-migratorias`). El prefix
    `/api/pasajeros/` público sólo lo agrega el nginx del API Gateway para
    llamadas externas; internamente entre servicios (MS4 → MS1 vía nombre de
    servicio docker) se llama al path sin prefix.
    """

    async def get_tickets_de_vuelo(self, vuelo_id: int) -> list[dict[str, Any]]:
        """`GET /tickets?vuelo_id={id}` — tickets del vuelo desde MS1 real."""
        response = await _client.get(f"/tickets?vuelo_id={vuelo_id}")
        response.raise_for_status()
        return response.json()

    async def health_check(self) -> dict[str, Any]:
        return await _client.health_check()


ms1_client = MS1Client()
