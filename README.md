# ms4-manifiesto-api

MS4 — Manifiesto de Vuelo · Python + FastAPI (sin BD)

Parte del Proyecto Parcial CS2032 — Cloud Computing (2026-2).
Contexto y arquitectura: [`cloud-computing-proyecto`](https://github.com/btoroled/cloud-computing-proyecto) ·
Plan de tareas: [`plan/backend.md` §7](https://github.com/btoroled/cloud-computing-proyecto/blob/main/docs/plan/backend.md) ·
Dueño: Fabricio.

## Estado (MS4-01 ✅)

Scaffold operativo: `GET /health` responde y `GET /health/dependencias` chequea MS1/MS2/MS3 en paralelo. Endpoints de manifiesto devuelven `501` (llegan en MS4-02, F1).

Ya trae (base de plantilla, BE-TX-02): `.editorconfig`, `.github/workflows/build-push-ghcr.yml` (el `.gitignore` de Python ya existía). Fuente: [plantilla común](https://github.com/Cloud-MLA/aeropuerto-infra-deploy/tree/main/plantilla).

Añadido en el scaffold (MS4-01):
- `app/main.py` — FastAPI 0.115 con Swagger en `/docs`.
- `app/config.py` — `pydantic-settings`, URLs de MS1/MS2/MS3 por env.
- `app/clients/base.py` — cliente HTTP compartido con timeout + reintentos exponenciales (BE-TX-09; retry solo en timeout/5xx/connection error).
- `app/routers/health.py` — `/health` y `/health/dependencias` (chequeo en paralelo con `asyncio.gather`).
- `app/routers/manifiesto.py` — 3 endpoints stub `501` (MS4-02/03 en F1/F2).
- `Dockerfile` multi-stage, no-root, `HEALTHCHECK` nativo.
- `docker-compose.yml` para dev local.
- `openapi.yaml` borrador (BE-TX-03).
- `tests/test_health.py` — 3 tests que pasan.

## Correr localmente

```bash
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
copy .env.example .env       # Windows (o cp en Linux)
uvicorn app.main:app --reload --port 8004
```

Abre http://localhost:8004/docs.

## Correr con Docker

```bash
docker compose up --build
```

## Correr tras corte de sesión del Learner Lab (<15 min)

```bash
git pull                                  # trae imagen actualizada
docker compose pull && docker compose up  # imagen ya publicada en GHCR
```

## Convenciones

- **Puerto interno:** `8004`. **Sin base de datos.**
- **Errores:** [contrato común](https://github.com/btoroled/cloud-computing-proyecto/blob/main/docs/contratos/errores.md).
  MS4 puede devolver **200 con `warnings[]`** si una dependencia no crítica falla (MS3 caído → manifiesto sin incidencias). Esto llega en MS4-04.
- **Imagen:** `git tag vX.Y && git push --tags` → `ghcr.io/cloud-mla/ms4-manifiesto-api:vX.Y`.

## Configuración (env vars)

Ver `.env.example`.

| Variable | Default | Descripción |
|---|---|---|
| `PORT` | `8004` | Puerto interno del servicio |
| `MS1_BASE_URL` | `http://ms1-pasajeros-api:8001` | Base URL de MS1 (sin sufijo `/api/...`) |
| `MS2_BASE_URL` | `http://ms2-vuelos-api:8002` | Base URL de MS2 |
| `MS3_BASE_URL` | `http://ms3-infraestructura-api:8003` | Base URL de MS3 |
| `HTTP_TIMEOUT_SECONDS` | `3` | Timeout de cada llamada saliente |
| `HTTP_RETRIES` | `2` | Reintentos ante fallo transitorio |
| `LOG_LEVEL` | `info` | `debug`/`info`/`warning`/`error` |
| `ENV` | `local` | Nombre del entorno |

## Endpoints

Base path de negocio: `/api/manifiesto`.

| Método | Ruta | Descripción | Estado |
|---|---|---|---|
| GET | `/health` | Estado propio | ✅ |
| GET | `/health/dependencias` | Estado de MS1/MS2/MS3 | ✅ |
| GET | `/manifiesto/{vuelo_id}` | Agrega vuelo+aeronave+aerolínea (MS2), pasajeros+ticket+checkin+equipaje (MS1), tripulación (MS2), recursos+incidencias abiertas (MS3) | ⏳ MS4-02 (F1) |
| GET | `/manifiesto/{vuelo_id}/pasajeros`, `/resumen` | Subrecursos y conteos | ⏳ MS4-03 (F2) |

Swagger-UI en `/docs` · OpenAPI JSON en `/openapi.json`.

Ver el [checklist personal de Fabricio](https://github.com/btoroled/cloud-computing-proyecto/blob/main/docs/plan/personas/fabricio.md) en el repo de docs.
