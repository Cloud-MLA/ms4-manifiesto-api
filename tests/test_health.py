"""Smoke test del scaffold. Corre con: pytest -q"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_up():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "up", "service": "ms4-manifiesto-api"}


def test_openapi_disponible():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    body = response.json()
    assert body["info"]["title"] == "MS4 — Manifiesto de Vuelo"


def test_manifiesto_stub_devuelve_501():
    response = client.get("/api/manifiesto/1234")
    assert response.status_code == 501
    assert response.json()["detail"]["tarea"] == "MS4-02"
