"""Servicio de agregación del manifiesto de vuelo (MS4-02 + MS4-04).

Estrategia:
1. Verifica que el vuelo exista en MS2 con una llamada corta (`/vuelos/{id}/exists`).
   Si no existe → 404 sin gastar más llamadas.
2. Lanza en PARALELO las 4 llamadas pesadas con `asyncio.gather(return_exceptions=True)`.
3. Si una dependencia falla, la excepción NO propaga — se registra en `warnings[]` y
   el campo correspondiente queda vacío. Esto cumple MS4-04.
"""
import asyncio
import logging
from typing import Any

import httpx

from app.clients.base import DependencyError
from app.clients.ms1 import ms1_client
from app.clients.ms2 import ms2_client
from app.clients.ms3 import ms3_client

logger = logging.getLogger(__name__)


class VueloNoExiste(Exception):
    """MS2 devolvió que el vuelo no existe — MS4 responde 404."""


async def obtener_manifiesto(vuelo_id: int) -> dict[str, Any]:
    """Devuelve el manifiesto agregado del vuelo. Puede incluir `warnings[]`.

    Raises:
        VueloNoExiste: si `/vuelos/{id}/exists` devolvió false.
    """
    if not await ms2_client.vuelo_exists(vuelo_id):
        raise VueloNoExiste(f"Vuelo {vuelo_id} no encontrado en MS2")

    vuelo, tickets, tripulacion, incidencias = await asyncio.gather(
        ms2_client.get_vuelo_completo(vuelo_id),
        ms1_client.get_tickets_de_vuelo(vuelo_id),
        ms2_client.get_tripulacion_de_vuelo(vuelo_id),
        ms3_client.get_incidencias_abiertas_de_vuelo(vuelo_id),
        return_exceptions=True,
    )

    warnings: list[str] = []

    def _resolver(nombre: str, resultado, fallback):
        """Si el resultado es Exception, registra warning y devuelve fallback."""
        if isinstance(resultado, (DependencyError, httpx.HTTPError)):
            msg = f"{nombre}: {resultado}"
            logger.warning("manifiesto vuelo=%s %s", vuelo_id, msg)
            warnings.append(msg)
            return fallback
        if isinstance(resultado, Exception):
            # Error no previsto — lo logueamos pero no dejamos caer la request.
            logger.exception(
                "manifiesto vuelo=%s error inesperado en %s", vuelo_id, nombre,
            )
            warnings.append(f"{nombre}: error inesperado ({type(resultado).__name__})")
            return fallback
        return resultado

    return {
        "vuelo_id": vuelo_id,
        "vuelo": _resolver("MS2/vuelo", vuelo, None),
        "pasajeros": _resolver("MS1/tickets", tickets, []),
        "tripulacion": _resolver("MS2/tripulacion", tripulacion, []),
        "incidencias_abiertas": _resolver("MS3/incidencias", incidencias, []),
        "warnings": warnings,
    }


async def obtener_pasajeros(vuelo_id: int) -> dict[str, Any]:
    """`/manifiesto/{id}/pasajeros` — solo los pasajeros del vuelo."""
    if not await ms2_client.vuelo_exists(vuelo_id):
        raise VueloNoExiste(f"Vuelo {vuelo_id} no encontrado en MS2")

    tickets = await ms1_client.get_tickets_de_vuelo(vuelo_id)
    return {"vuelo_id": vuelo_id, "pasajeros": tickets, "total": len(tickets)}


async def obtener_resumen(vuelo_id: int) -> dict[str, Any]:
    """`/manifiesto/{id}/resumen` — conteos: pax, kg equipaje, incidencias abiertas."""
    manifiesto = await obtener_manifiesto(vuelo_id)
    pasajeros = manifiesto["pasajeros"] or []
    incidencias = manifiesto["incidencias_abiertas"] or []

    pax_total = len(pasajeros)
    equipaje_kg_total = sum(
        float(eq.get("peso", 0))
        for p in pasajeros
        for eq in (p.get("equipaje") or [])
    )

    return {
        "vuelo_id": vuelo_id,
        "pasajeros_total": pax_total,
        "equipaje_kg_total": round(equipaje_kg_total, 2),
        "incidencias_abiertas": len(incidencias),
        "warnings": manifiesto["warnings"],
    }
