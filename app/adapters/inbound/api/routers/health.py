"""
Router de Health Check
"""
from fastapi import APIRouter
from datetime import datetime
from app.config.settings import get_settings
from app.config.check_connection import check_database_connection

router = APIRouter()
settings = get_settings()


@router.get("/health")
async def health_check():
    """
    Endpoint de health check para verificar que la API está funcionando
    Incluye información del entorno actual
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.version,
        "app_name": settings.app_name,
        "environment": settings.environment,
        "debug": settings.debug,
        "database": settings.database_url.split('@')[-1] if '@' in settings.database_url else "local"
    }


@router.get("/health/database")
async def database_health():
    """
    Endpoint para verificar la conexión a la base de datos
    """
    is_connected = check_database_connection()  # Verificar la conexión a la base de datos
    if is_connected:
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    else:
        return {
            "status": "unhealthy",
            "database": "not connected",
            "timestamp": datetime.utcnow().isoformat()
        }