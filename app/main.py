"""Entry point de MS4 — Manifiesto de Vuelo."""
import logging

from fastapi import FastAPI

from app.config import settings
from app.routers import health, manifiesto

logging.basicConfig(
    level=settings.log_level.upper(),  # logging.basicConfig espera mayúsculas
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title="MS4 — Manifiesto de Vuelo",
    version="0.1.0",
    description=(
        "Agrega en una sola respuesta el vuelo (MS2), pasajeros y equipaje (MS1) "
        "y recursos e incidencias (MS3). Este microservicio no tiene base de datos "
        "propia — solo compone respuestas HTTP."
    ),
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.include_router(health.router)
app.include_router(manifiesto.router)
