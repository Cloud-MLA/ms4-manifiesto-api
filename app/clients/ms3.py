"""Cliente de MS3 — Infraestructura / Incidencias."""
from typing import Any

from app.clients.base import HttpClient
from app.config import settings

_client = HttpClient(
    base_url=settings.ms3_base_url,
    timeout_seconds=settings.http_timeout_seconds,
    retries=settings.http_retries,
    service_name="MS3",
)


class MS3Client:
    """Métodos que MS4 usa contra MS3.

    Nota de despliegue: MS3 real (Edinson, Express) no aplica los filtros
    `?vuelo_id=` ni `?abierta=` al listar incidencias — devuelve el catálogo
    completo (~25 000 documentos). MS4 filtra localmente por `vuelo_id` (que
    aparece dentro de cada `incidencia.retrasa_vuelos[]`) y por
    `fecha_cierre == null` (criterio de "abierta").
    """

    async def get_asignaciones_de_vuelo(self, vuelo_id: int) -> list[dict[str, Any]]:
        """`GET /api/infra/asignaciones?vuelo_id={id}` — recursos asignados al vuelo."""
        response = await _client.get(f"/api/infra/asignaciones?vuelo_id={vuelo_id}")
        response.raise_for_status()
        return response.json()

    async def get_incidencias_abiertas_de_vuelo(self, vuelo_id: int) -> list[dict[str, Any]]:
        """Lista todas las incidencias en MS3 y filtra en el cliente.

        MS3 real ignora los filtros `?vuelo_id=` y `?abierta=`; devolvería el
        catálogo completo si no se procesa. Aquí se traen todas (~25 000) y
        se conservan solo las que:
          1. Tienen `fecha_cierre` null (abiertas), y
          2. Incluyen `vuelo_id` en el arreglo `retrasa_vuelos[]`.

        En el mediano plazo esto debe delegarse a MS3 (que Edinson filtre en
        Mongo con `.find({retrasa_vuelos: {$elemMatch: {vuelo_id: X}}, fecha_cierre: null})`);
        el filtrado local es la solución para la demo del Hito 2.
        """
        response = await _client.get("/api/infra/incidencias")
        response.raise_for_status()
        todas = response.json()
        return [
            inc for inc in todas
            if inc.get("fecha_cierre") in (None, "")
            and any(v.get("vuelo_id") == vuelo_id for v in inc.get("retrasa_vuelos", []))
        ]

    async def health_check(self) -> dict[str, Any]:
        return await _client.health_check()


ms3_client = MS3Client()
