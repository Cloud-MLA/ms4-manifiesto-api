"""Cliente HTTP asíncrono compartido con timeout y reintentos.

Este cliente lo comparten los 3 clientes de MS1/MS2/MS3 (y también lo usará
MS1 para llamar a MS2 y MS3 para llamar a MS2, según el plan BE-TX-09).
"""
import asyncio
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class DependencyError(Exception):
    """Error al llamar a un microservicio dependiente (agotó reintentos)."""


class HttpClient:
    """Wrapper minimalista de httpx.AsyncClient con reintentos exponenciales.

    Los reintentos aplican solo a errores transitorios (timeout, 5xx, connection).
    Un 4xx del upstream (por ejemplo 404 vuelo inexistente) se propaga tal cual.
    """

    def __init__(self, base_url: str, timeout_seconds: float, retries: int, service_name: str):
        self._base_url = base_url.rstrip("/")
        self._timeout = httpx.Timeout(timeout_seconds)
        self._retries = retries
        self._service = service_name

    async def get(self, path: str, **kwargs) -> httpx.Response:
        return await self._request("GET", path, **kwargs)

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        url = f"{self._base_url}{path}"
        last_exc: Exception | None = None
        for intento in range(self._retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.request(method, url, **kwargs)
                # 5xx cuenta como transitorio y se reintenta
                if response.status_code >= 500 and intento < self._retries:
                    logger.warning(
                        "%s %s %s -> %s (reintento %s/%s)",
                        method, url, self._service, response.status_code,
                        intento + 1, self._retries,
                    )
                    await asyncio.sleep(2**intento * 0.1)
                    continue
                return response
            except (httpx.TimeoutException, httpx.ConnectError, httpx.ReadError) as exc:
                last_exc = exc
                if intento < self._retries:
                    logger.warning(
                        "%s %s %s: %s (reintento %s/%s)",
                        method, url, self._service, exc,
                        intento + 1, self._retries,
                    )
                    await asyncio.sleep(2**intento * 0.1)
                    continue
                raise DependencyError(f"{self._service} inalcanzable: {exc}") from exc
        raise DependencyError(f"{self._service} inalcanzable: {last_exc}")

    async def health_check(self) -> dict[str, Any]:
        """Devuelve un dict con status (up|degraded|down) y detalle opcional."""
        try:
            response = await self.get("/health")
            if response.status_code == 200:
                return {"status": "up"}
            return {"status": "degraded", "detail": f"HTTP {response.status_code}"}
        except DependencyError as exc:
            return {"status": "down", "detail": str(exc)}
