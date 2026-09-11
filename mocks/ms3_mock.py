"""Mock de MS3 — Infraestructura / Incidencias."""
from fastapi import FastAPI

from mocks.data import asignaciones, incidencias_abiertas

app = FastAPI(title="MS3 mock")


@app.get("/health")
def health():
    return {"status": "up", "service": "ms3-mock"}


@app.get("/api/infra/incidencias")
def get_incidencias(vuelo_id: int, abierta: bool = False):
    return incidencias_abiertas(vuelo_id)


@app.get("/api/infra/asignaciones")
def get_asignaciones(vuelo_id: int):
    return asignaciones(vuelo_id)
