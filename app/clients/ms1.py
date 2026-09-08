"""Cliente de MS1 — Pasajeros / Tickets."""
from app.clients.base import HttpClient
from app.config import settings

ms1_client = HttpClient(
    base_url=settings.ms1_base_url,
    timeout_seconds=settings.http_timeout_seconds,
    retries=settings.http_retries,
    service_name="MS1",
)
