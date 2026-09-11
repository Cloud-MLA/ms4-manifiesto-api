"""Tests del manifiesto usando httpx.MockTransport para simular MS1/MS2/MS3.

MockTransport intercepta las requests HTTP en memoria — no levanta servidores
externos. Ejecuta el mismo código de app.services.manifiesto sin cambios.

Estos tests validan MS4-02 (endpoint principal) y MS4-04 (warnings[] cuando
alguna dependencia cae).
"""
import httpx
import pytest
from fastapi.testclient import TestClient

from app.clients import base as base_client_module
from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Fixtures — MockTransport monkeypatched sobre httpx.AsyncClient
# ---------------------------------------------------------------------------
def _fixture_vuelo(vuelo_id: int) -> dict:
    return {
        "id": vuelo_id,
        "num_vuelo": "LA0032",
        "estado": "Aterrizado",
        "tipo": "Internacional",
        "origen": "LIM",
        "destino": "SCL",
        "aeronave": {"placa": "OB-1111", "modelo": "Boeing 787-9", "clase": "E"},
        "aerolinea": {"ruc": "20100000018", "nombre": "GOL", "alianza": "Ninguna"},
    }


def _fixture_tickets() -> list[dict]:
    return [
        {
            "id_ticket": 1, "id_persona": 134482, "estado_boarding": "Embarcado",
            "equipaje": [{"id": "BHS0000000001", "peso": "17.65"}],
        },
        {
            "id_ticket": 2, "id_persona": 158084, "estado_boarding": "Embarcado",
            "equipaje": [{"id": "BHS0000000002", "peso": "12.10"},
                          {"id": "BHS0000000003", "peso": "8.50"}],
        },
    ]


def _handler_todo_ok(request: httpx.Request) -> httpx.Response:
    """Devuelve respuestas exitosas para todas las rutas usadas por MS4-02."""
    url = str(request.url)
    if "/vuelos/6058/exists" in url:
        return httpx.Response(200, json={"exists": True})
    if "/vuelos/6058/tripulacion" in url:
        return httpx.Response(200, json=[
            {"id_empleado": 1542, "nombre": "Carlos", "num_licencia": "DGAC-001542"},
        ])
    if "/vuelos/6058" in url:
        return httpx.Response(200, json=_fixture_vuelo(6058))
    if "/tickets" in url and "vuelo_id=6058" in url:
        return httpx.Response(200, json=_fixture_tickets())
    if "/incidencias" in url and "vuelo_id=6058" in url:
        return httpx.Response(200, json=[
            {"id": 1, "gravedad": "Alta", "tipo_incidencia": "Falta_Combustible",
             "fecha_cierre": None},
        ])
    if "/vuelos/99999/exists" in url:
        return httpx.Response(200, json={"exists": False})
    return httpx.Response(404)


def _handler_ms3_caido(request: httpx.Request) -> httpx.Response:
    """Como _handler_todo_ok pero MS3 falla — para probar warnings[]."""
    url = str(request.url)
    if ":8003" in url or "/infra/" in url or "/incidencias" in url:
        raise httpx.ConnectError("Simulacion: MS3 caido")
    return _handler_todo_ok(request)


@pytest.fixture
def mock_todo_ok(monkeypatch):
    original_init = httpx.AsyncClient.__init__

    def patched_init(self, *args, **kwargs):
        kwargs["transport"] = httpx.MockTransport(_handler_todo_ok)
        original_init(self, *args, **kwargs)

    monkeypatch.setattr(httpx.AsyncClient, "__init__", patched_init)
    yield


@pytest.fixture
def mock_ms3_caido(monkeypatch):
    original_init = httpx.AsyncClient.__init__

    def patched_init(self, *args, **kwargs):
        kwargs["transport"] = httpx.MockTransport(_handler_ms3_caido)
        original_init(self, *args, **kwargs)

    # Reducir retries a 0 para que la prueba corra rápido
    monkeypatch.setattr(base_client_module.HttpClient, "_retries", 0, raising=False)
    monkeypatch.setattr(httpx.AsyncClient, "__init__", patched_init)
    yield


# ---------------------------------------------------------------------------
# Casos felices
# ---------------------------------------------------------------------------
def test_manifiesto_agrega_los_4_dominios(mock_todo_ok):
    response = client.get("/api/manifiesto/6058")
    assert response.status_code == 200
    body = response.json()
    assert body["vuelo_id"] == 6058
    assert body["vuelo"]["num_vuelo"] == "LA0032"
    assert len(body["pasajeros"]) == 2
    assert len(body["tripulacion"]) == 1
    assert len(body["incidencias_abiertas"]) == 1
    assert body["warnings"] == []


def test_resumen_calcula_conteos(mock_todo_ok):
    response = client.get("/api/manifiesto/6058/resumen")
    assert response.status_code == 200
    body = response.json()
    assert body["pasajeros_total"] == 2
    # 17.65 + 12.10 + 8.50 = 38.25
    assert body["equipaje_kg_total"] == 38.25
    assert body["incidencias_abiertas"] == 1


def test_pasajeros_endpoint(mock_todo_ok):
    response = client.get("/api/manifiesto/6058/pasajeros")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert body["pasajeros"][0]["id_ticket"] == 1


# ---------------------------------------------------------------------------
# 404 cuando el vuelo no existe
# ---------------------------------------------------------------------------
def test_vuelo_inexistente_devuelve_404(mock_todo_ok):
    response = client.get("/api/manifiesto/99999")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# MS4-04: dependencia caída → warning + respuesta parcial (no 500)
# ---------------------------------------------------------------------------
def test_ms3_caido_devuelve_manifiesto_con_warning(mock_ms3_caido):
    response = client.get("/api/manifiesto/6058")
    assert response.status_code == 200
    body = response.json()
    # El vuelo (MS2), pasajeros (MS1) y tripulacion (MS2) sí llegaron:
    assert body["vuelo"]["num_vuelo"] == "LA0032"
    assert len(body["pasajeros"]) == 2
    assert len(body["tripulacion"]) == 1
    # Incidencias vacío porque MS3 cayó:
    assert body["incidencias_abiertas"] == []
    # Y hay un warning que dice que MS3 falló:
    assert len(body["warnings"]) == 1
    assert "MS3" in body["warnings"][0]
