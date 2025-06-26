"""
Configuración de la aplicación usando Pydantic Settings
"""
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """
    Configuración de la aplicación
    """
    # Configuración de la aplicación
    app_name: str = Field(default="CRM Backend", env="APP_NAME")
    debug: bool = Field(default=False, env="DEBUG")
    version: str = Field(default="1.0.0", env="VERSION")
    
    # Configuración de la base de datos
    database_url: str = Field(
        default="mysql+pymysql://root:EQlQpqrJgNXElaRCVLnJlmvYNjgQWbDX@junction.proxy.rlwy.net:31940/railway",
        env="DATABASE_URL"
    )
    database_host: str = Field(default="localhost", env="DATABASE_NAME")
    database_port: int = Field(default=31940, env="DATABASE_PORT")
    database_user: str = Field(default="user", env="DATABASE_USER")
    database_password: str = Field(default="password", env="DATABASE_PASSWORD")
    database_name: str = Field(default="crm_db", env="DATABASE_NAME")
    

    
    # Configuración de CORS
    cors_origins: str = Field(default="*", env="CORS_ORIGINS")
    
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