"""Cliente de MS2 — Vuelos / Operaciones."""
from app.clients.base import HttpClient
from app.config import settings

ms2_client = HttpClient(
    base_url=settings.ms2_base_url,
    timeout_seconds=settings.http_timeout_seconds,
    retries=settings.http_retries,
    service_name="MS2",
)
