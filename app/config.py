"""Configuración leída de variables de entorno (12-factor)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Config de MS4 — Manifiesto de Vuelo.

    Todos los campos pueden sobreescribirse con variables de entorno del mismo
    nombre. Ver `.env.example`.

    Puertos por convención del equipo: MS1=8001, MS2=8002, MS3=8003, MS4=8004.
    """

    port: int = 8004
    env: str = "local"

    ms1_base_url: str = "http://ms1-pasajeros-api:8001"
    ms2_base_url: str = "http://ms2-vuelos-api:8002"
    ms3_base_url: str = "http://ms3-infraestructura-api:8003"

    http_timeout_seconds: float = 3.0
    http_retries: int = 2

    log_level: str = "info"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
