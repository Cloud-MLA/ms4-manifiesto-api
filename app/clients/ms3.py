"""Cliente de MS3 — Infraestructura / Incidencias."""
from app.clients.base import HttpClient
from app.config import settings

ms3_client = HttpClient(
    base_url=settings.ms3_base_url,
    timeout_seconds=settings.http_timeout_seconds,
    retries=settings.http_retries,
    service_name="MS3",
)
