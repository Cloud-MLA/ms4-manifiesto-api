"""Mock de MS2 — Vuelos / Operaciones."""
from fastapi import FastAPI, HTTPException, Response

from mocks.data import tripulacion, vuelo

app = FastAPI(title="MS2 mock")

# Vuelos "inexistentes" para probar el 404 de MS4
VUELOS_INEXISTENTES = {99999}


@app.get("/health")
def health():
    return {"status": "up", "service": "ms2-mock"}


@app.get("/api/vuelos/{vuelo_id}/exists")
def vuelo_exists(vuelo_id: int, response: Response):
    if vuelo_id in VUELOS_INEXISTENTES:
        response.status_code = 404
        return {"exists": False}
    return {"exists": True}


@app.get("/api/vuelos/{vuelo_id}")
def get_vuelo(vuelo_id: int):
    if vuelo_id in VUELOS_INEXISTENTES:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")
    return vuelo(vuelo_id)


@app.get("/api/vuelos/{vuelo_id}/tripulacion")
def get_tripulacion(vuelo_id: int):
    return tripulacion(vuelo_id)
