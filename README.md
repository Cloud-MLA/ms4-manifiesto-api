# ms4-manifiesto-api
MS4 — Manifiesto de Vuelo · Python + FastAPI (sin BD)

Parte del Proyecto Parcial CS2032 — Cloud Computing (2026-2).
Contexto y arquitectura: [`cloud-computing-proyecto`](https://github.com/btoroled/cloud-computing-proyecto) ·
Plan de tareas: [`plan/backend.md` §7](https://github.com/btoroled/cloud-computing-proyecto/blob/main/docs/plan/backend.md) ·
Dueño: Fabricio.

## Puesta en marcha (base desde la plantilla · BE-TX-02)

Ya trae: `.editorconfig`, `.env.example`, `.github/workflows/build-push-ghcr.yml`
(el `.gitignore` de Python ya existía). Fuente: [plantilla común](https://github.com/Cloud-MLA/aeropuerto-infra-deploy/tree/main/plantilla).

**Pendiente de scaffold (MS4-01, Fabricio):**
- Copiar `plantilla/docker/Dockerfile.python` como `Dockerfile` (sin servicio de BD en el compose).
- Cliente HTTP compartido (timeout, reintento, propagación de error — BE-TX-09).
- `GET /health/dependencias` (estado de MS1/MS2/MS3) y `GET /docs`.
- `openapi.yaml` borrador (BE-TX-03).

## Convenciones

- **Puerto interno:** `8004`. **Sin base de datos.**
- **Errores:** [contrato común](https://github.com/btoroled/cloud-computing-proyecto/blob/main/docs/contratos/errores.md).
  MS4 puede devolver **200 con `warnings[]`** si una dependencia no crítica falla (MS3 caído → manifiesto sin incidencias).
- **Imagen:** `git tag vX.Y && git push --tags` → `ghcr.io/cloud-mla/ms4-manifiesto-api:vX.Y`.

## Endpoints (previstos)

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health/dependencias` | Estado de MS1/MS2/MS3 |
| GET | `/manifiesto/{vuelo_id}` | Agrega vuelo+aeronave+aerolínea (MS2), pasajeros+ticket+checkin+equipaje (MS1), tripulación (MS2), recursos+incidencias abiertas (MS3) |
| GET | `/manifiesto/{vuelo_id}/pasajeros`, `/resumen` | Subrecursos y conteos |
