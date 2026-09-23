"""Mock de MS3 — Infraestructura / Incidencias."""
from fastapi import FastAPI

from mocks.data import asignaciones, incidencias_abiertas

app = FastAPI(title="MS3 mock")


@app.get("/health")
def health():
    return {"status": "up", "service": "ms3-mock"}


# MS3 real (Edinson) ignora los filtros ?vuelo_id= y ?abierta=; devuelve todas.
# El cliente MS4 filtra localmente.
@app.get("/api/infra/incidencias")
def get_incidencias():
    # Datos representativos: una abierta relacionada al vuelo, una cerrada,
    # una abierta no relacionada. MS4 debe conservar solo la primera.
    return [
        {"id": 1, "gravedad": "Alta", "tipo_incidencia": "Falta_Combustible",
         "fecha_cierre": None, "retrasa_vuelos": [{"vuelo_id": 6058}]},
        {"id": 2, "gravedad": "Leve", "tipo_incidencia": "Inundacion",
         "fecha_cierre": "2026-09-06T03:44:42Z", "retrasa_vuelos": [{"vuelo_id": 6058}]},
        {"id": 3, "gravedad": "Moderada", "tipo_incidencia": "Falla_Radar",
         "fecha_cierre": None, "retrasa_vuelos": [{"vuelo_id": 12345}]},
    ] + incidencias_abiertas(0)  # noqa: por compatibilidad con la fixture


@app.get("/api/infra/asignaciones")
def get_asignaciones(vuelo_id: int):
    return asignaciones(vuelo_id)
