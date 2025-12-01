"""
Configuración de la aplicación usando Pydantic Settings
"""
from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional
from urllib.parse import urlparse

from pydantic import Field, model_validator
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
    async_database_url: Optional[str] = Field(default=None, env="ASYNC_DATABASE_URL")
    database_host: Optional[str] = Field(default=None, env="DATABASE_HOST")
    database_port: Optional[int] = Field(default=None, env="DATABASE_PORT")
    database_user: Optional[str] = Field(default=None, env="DATABASE_USER")
    database_password: Optional[str] = Field(default=None, env="DATABASE_PASSWORD")
    database_name: Optional[str] = Field(default=None, env="DATABASE_NAME")
    
    @model_validator(mode='after')
    def parse_database_url(self):
        """
        Si las variables individuales de la base de datos no están configuradas,
        las extrae automáticamente de DATABASE_URL (útil para Railway).
        """
        if self.database_url and not self.async_database_url:
            parsed = urlparse(self.database_url)
            
            # Construir async_database_url reemplazando postgresql:// por postgresql+asyncpg://
            if self.database_url.startswith("postgresql://"):
                self.async_database_url = self.database_url.replace(
                    "postgresql://", "postgresql+asyncpg://", 1
                )
            elif self.database_url.startswith("postgres://"):
                self.async_database_url = self.database_url.replace(
                    "postgres://", "postgresql+asyncpg://", 1
                )
            else:
                self.async_database_url = self.database_url
            
            # Extraer componentes individuales
            if not self.database_host:
                self.database_host = parsed.hostname or "localhost"
            if not self.database_port:
                self.database_port = parsed.port or 5432
            if not self.database_user:
                self.database_user = parsed.username or ""
            if not self.database_password:
                self.database_password = parsed.password or ""
            if not self.database_name:
                self.database_name = parsed.path.lstrip("/") if parsed.path else ""
        
        return self

    # Configuración de CORS
    cors_origins: str = Field(default="*", env="CORS_ORIGINS")

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
    aws_access_key_id: str = Field(default="", env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(default="", env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    aws_bucket_name: str = Field(default="", env="AWS_BUCKET_NAME")

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
