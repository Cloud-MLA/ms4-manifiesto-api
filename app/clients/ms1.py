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
    `/api/pasajeros/` público lo agrega el nginx del API Gateway y también
    el nginx interno de VM-PROD (ver `aeropuerto-infra-deploy/nginx/nginx.conf`
    → `location /api/pasajeros/ { proxy_pass http://ms1/; }`).

    Por eso `MS1_BASE_URL` en producción apunta a `http://nginx` (no a
    `http://ms1:8001` directo) — así el prefix `/api/pasajeros/` se conserva
    en el path y el nginx lo strippea antes de reenviar a MS1.
    """

    async def get_tickets_de_vuelo(self, vuelo_id: int) -> list[dict[str, Any]]:
        """`GET /api/pasajeros/tickets?vuelo_id={id}` a través del nginx interno."""
        response = await _client.get(f"/api/pasajeros/tickets?vuelo_id={vuelo_id}")
        response.raise_for_status()
        return response.json()

    async def health_check(self) -> dict[str, Any]:
        return await _client.health_check()


ms1_client = MS1Client()
