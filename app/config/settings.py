"""
Configuración de la aplicación usando Pydantic Settings
"""
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, Literal
from dotenv import load_dotenv
import os

class Settings(BaseSettings):
    """
    Configuración de la aplicación con soporte para múltiples entornos
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

    load_dotenv()

    # Configuración de la base de datos
    database_url: str = Field(
        default="sqlite:///./crm_local.db",  # Base de datos local por defecto
        env="DATABASE_URL"
    )
    async_database_url: str = Field(
        default="sqlite+aiosqlite:///./crm_local.db",
        env="ASYNC_DATABASE_URL"
    )
    database_host: str = Field(default="localhost", env="DATABASE_HOST")
    database_port: int = Field(default=3306, env="DATABASE_PORT")
    database_user: str = Field(default="root", env="DATABASE_USER")
    database_password: str = Field(default="password", env="DATABASE_PASSWORD")
    database_name: str = Field(default="crm_db", env="DATABASE_NAME")



    # Configuración de CORS
    cors_origins: str = Field(default="*", env="CORS_ORIGINS")

    # Configuración de eventos asíncronos
    evento_financiero_max_workers: int = Field(
        default=20,
        env="EVENTO_FINANCIERO_MAX_WORKERS",
        description="Número máximo de workers para eventos financieros"
    )
    evento_financiero_timeout: int = Field(
        default=300,  # 5 minutos
        env="EVENTO_FINANCIERO_TIMEOUT",
        description="Timeout en segundos para apagar workers"
    )

    @property
    def is_development(self) -> bool:
        """Verifica si está en modo desarrollo"""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Verifica si está en modo producción"""
        return self.environment == "production"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    """
    Obtener configuración de la aplicación (singleton)
    """
    return Settings() 