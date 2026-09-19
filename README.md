# ms4-manifiesto-api · v1.0

**MS4 — Manifiesto de Vuelo.** Microservicio agregador HTTP **sin base de datos** que consolida en una sola respuesta:

- **Vuelo + aeronave + aerolínea** (MS2 · PostgreSQL)
- **Tickets + pasajero + check-in + equipaje** (MS1 · MySQL)
- **Tripulación asignada** (MS2)
- **Incidencias abiertas del vuelo** (MS3 · MongoDB)

Parte del Proyecto Parcial CS2032 — Cloud Computing (UTEC 2026-2).
[`cloud-computing-proyecto`](https://github.com/btoroled/cloud-computing-proyecto) ·
[`plan/hito2.md §2.5`](https://github.com/btoroled/cloud-computing-proyecto/blob/main/docs/plan/hito2.md#25-ms4--manifiesto-de-vuelo--python--fastapi-sin-bd-fabricio) ·
Dueño: **Fabricio**.

---

## Endpoints

Base path: `/api/manifiesto`.

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/health` | Estado propio |
| `GET` | `/health/dependencias` | Estado de MS1, MS2 y MS3 (chequeo en paralelo) |
| `GET` | `/api/manifiesto/{vuelo_id}` | Manifiesto consolidado |
| `GET` | `/api/manifiesto/{vuelo_id}/pasajeros` | Subrecurso: solo pasajeros |
| `GET` | `/api/manifiesto/{vuelo_id}/resumen` | Conteos: pax, equipaje kg, incidencias abiertas |
| `GET` | `/docs` · `/openapi.json` | Swagger-UI navegable |

## Ejemplo `curl`

```bash
# Manifiesto completo
curl https://<api-gateway>/api/manifiesto/6058

# Resumen (solo conteos)
curl https://<api-gateway>/api/manifiesto/6058/resumen

# Ver estado de dependencias
curl https://<api-gateway>/api/manifiesto/health/dependencias
```

Respuesta del manifiesto (recortada):

```json
{
  "vuelo_id": 6058,
  "vuelo": {"id":6058,"numero":"LA0032","estado":"Aterrizado","tipo":"Internacional","origen":"LIM","destino":"SCL"},
  "pasajeros": [
    {"id_ticket":1,"id_persona":134482,"estado_boarding":"Embarcado","equipaje":[{"id":"BHS0000000001","peso":"17.65"}]}
  ],
  "tripulacion": [{"id_empleado":1542,"nombre":"Carlos","apellido":"Ruiz","num_licencia":"DGAC-001542"}],
  "incidencias_abiertas": [{"id":1,"gravedad":"Alta","tipo_incidencia":"Falta_Combustible","fecha_cierre":null}],
  "warnings": []
}
```

## Tolerancia a fallos (MS4-04)

Si alguna dependencia (MS1/MS2/MS3) no responde, MS4 devuelve **200 con datos parciales + `warnings[]`** en vez de fallar. Ejemplo con MS3 caído:

```json
{
  "vuelo_id": 6058,
  "vuelo": {...},
  "pasajeros": [...],
  "tripulacion": [...],
  "incidencias_abiertas": [],
  "warnings": ["MS3/incidencias: MS3 inalcanzable — connection error"]
}
```

Si el vuelo no existe en MS2, MS4 devuelve `404` sin gastar las demás llamadas.

---

## Correr localmente

**Sin Docker** (usa mocks internos de MS1/MS2/MS3 vía env vars):

```bash
python -m venv .venv
.venv\Scripts\activate           # Windows
# source .venv/bin/activate      # Linux/Mac
pip install -r requirements.txt
copy .env.example .env            # Windows (o cp)
uvicorn app.main:app --reload --port 8004
```

Abre http://localhost:8004/docs.

**Con Docker + mocks de las 3 dependencias** (todo integrado):

```bash
docker compose -f mocks/docker-compose.mocks.yml up -d --build
curl http://localhost:8004/api/manifiesto/6058
docker compose -f mocks/docker-compose.mocks.yml down
```

Ver [`mocks/README.md`](mocks/README.md) para detalles.

**Contra los servicios reales** (Guillermo/Mariano/Edinson):

```bash
export MS1_BASE_URL=http://ms1:8001
export MS2_BASE_URL=http://ms2:8002
export MS3_BASE_URL=http://ms3:8003
docker compose up --build
```

## Correr tras corte de sesión del Learner Lab (<15 min)

```bash
git pull                                       # trae compose actualizado
docker compose pull && docker compose up -d    # imagen ya publicada en GHCR
```

---

## Configuración (env vars)

Ver `.env.example`.

| Variable | Default | Descripción |
|---|---|---|
| `PORT` | `8004` | Puerto interno del servicio |
| `MS1_BASE_URL` | `http://ms1-pasajeros-api:8001` | Base URL de MS1 |
| `MS2_BASE_URL` | `http://ms2-vuelos-api:8002` | Base URL de MS2 |
| `MS3_BASE_URL` | `http://ms3-infraestructura-api:8003` | Base URL de MS3 |
| `HTTP_TIMEOUT_SECONDS` | `3` | Timeout de cada llamada saliente |
| `HTTP_RETRIES` | `2` | Reintentos ante fallo transitorio |
| `LOG_LEVEL` | `info` | `debug`/`info`/`warning`/`error` |
| `ENV` | `local` | Nombre del entorno |

Convenciones del equipo (BE-TX-02 de Benja): `MS_BASE_URL` sin sufijo `/api/xxx` — el path completo va en cada cliente.

---

## Arquitectura interna

```
app/
├── main.py              FastAPI 0.115
├── config.py            pydantic-settings
├── clients/
│   ├── base.py          HttpClient async con timeout + reintentos exponenciales (BE-TX-09)
│   ├── ms1.py           GET /api/pasajeros/tickets?vuelo_id=
│   ├── ms2.py           GET /api/vuelos/{id}/exists, /{id}, /{id}/tripulacion
│   └── ms3.py           GET /api/infra/incidencias, /asignaciones
├── services/
│   └── manifiesto.py    Orquestador: asyncio.gather + warnings[] (MS4-02/03/04)
└── routers/
    ├── health.py        /health + /health/dependencias
    └── manifiesto.py    /api/manifiesto/{id} + /pasajeros + /resumen
tests/                   9 tests con httpx.MockTransport (no requieren Docker)
mocks/                   3 FastAPI mocks + compose para dev local
```

## Decisiones técnicas

- **`httpx.AsyncClient`** — permite `asyncio.gather` para chequear MS1/MS2/MS3 en paralelo.
- **Reintentos exponenciales** (0.1s, 0.2s) solo en errores transitorios: timeout, 5xx, connection. Un 4xx del upstream se propaga.
- **`DependencyError`** custom para separar "servicio caído" de "servicio respondió 4xx" — clave para MS4-04.
- **Config 12-factor** con Pydantic Settings y `.env.example` documentado.
- **Docker multi-stage** con usuario no-root, `HEALTHCHECK` nativo del contenedor.

---

## Tests

```bash
pytest -q
```

9 tests · 2 seg. Cubren:

- `test_health.py` — `/health` y `/openapi.json`.
- `test_manifiesto.py` — usa `httpx.MockTransport` (sin Docker):
  - Agregación de las 4 fuentes (feliz).
  - `/resumen` calcula conteos correctamente.
  - `/pasajeros` devuelve subset con `total`.
  - Vuelo inexistente → 404.
  - MS3 caído → manifiesto parcial (200) con `warnings[]`.

---

## Publicación de imagen

`git tag v1.0` + `git push --tags` dispara [`build-push-ghcr.yml`](.github/workflows/build-push-ghcr.yml) → publica `ghcr.io/cloud-mla/ms4-manifiesto-api:v1.0` y `:latest`.

En producción, `compose/vm-prod/docker-compose.yml` del repo [`aeropuerto-infra-deploy`](https://github.com/Cloud-MLA/aeropuerto-infra-deploy) hace `docker compose pull && up`.

---

## Convenciones del proyecto

- **Puerto interno:** `8004`. **Sin base de datos.**
- **Errores:** [contrato común](https://github.com/btoroled/cloud-computing-proyecto/blob/main/docs/contratos/errores.md).
- **Imagen:** `git tag vX.Y && git push --tags` → `ghcr.io/cloud-mla/ms4-manifiesto-api:vX.Y`.

Ver el [checklist personal de Fabricio](https://github.com/btoroled/cloud-computing-proyecto/blob/main/docs/plan/personas/fabricio.md) en el repo de docs.
