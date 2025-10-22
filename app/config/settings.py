"""
Configuración de la aplicación usando Pydantic Settings
"""
import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings

# --- Ruta al archivo .env ---
# Construye la ruta al directorio raíz del proyecto para encontrar el .env
BASE_DIR = Path(__file__).resolve().parent.parent.parent
dotenv_path = BASE_DIR / ".env"


class Settings(BaseSettings):
    """
    Configuración de la aplicación con soporte para múltiples entornos.
    Pydantic se encargará de leer el archivo especificado en `env_file`.
    """
    # Entorno de ejecución
    environment: Literal["development", "production", "staging"] = Field(
        default="development",
        env="ENVIRONMENT",
        description="Entorno de ejecución: development, production, staging"
    )

    # Configuración de la aplicación
    app_name: str = Field(default="CRM Backend", env="APP_NAME")
    debug: bool = Field(default=False, env="DEBUG")
    version: str = Field(default="1.0.0", env="VERSION")

    # Configuración de la base de datos
    database_url: str = Field(..., env="DATABASE_URL")
    async_database_url: str = Field(..., env="ASYNC_DATABASE_URL")
    database_host: str = Field(..., env="DATABASE_HOST")
    database_port: int = Field(..., env="DATABASE_PORT")
    database_user: str = Field(..., env="DATABASE_USER")
    database_password: str = Field(..., env="DATABASE_PASSWORD")
    database_name: str = Field(..., env="DATABASE_NAME")

    # Configuración de CORS
    cors_origins: str = Field(..., env="CORS_ORIGINS")

    # Configuración de eventos asíncronos
    evento_financiero_max_workers: int = Field(
        default=5,
        env="EVENTO_FINANCIERO_MAX_WORKERS",
        description="Número máximo de workers para eventos financieros"
    )
    evento_financiero_timeout: int = Field(
        default=60,
        env="EVENTO_FINANCIERO_TIMEOUT",
        description="Timeout en segundos para apagar workers"
    )

    # Configuración de AWS
    aws_access_key_id: str = Field(..., env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(..., env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(..., env="AWS_REGION")
    aws_bucket_name: str = Field(..., env="AWS_BUCKET_NAME")

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    class Config:
        # Le decimos a Pydantic que cargue las variables desde este archivo
        env_file = dotenv_path
        env_file_encoding = "utf-8"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    """
    Obtener configuración de la aplicación (singleton).
    """
    return Settings()
