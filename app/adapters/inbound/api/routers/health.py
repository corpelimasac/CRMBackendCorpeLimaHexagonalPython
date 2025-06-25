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
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.version,
        "app_name": settings.app_name
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