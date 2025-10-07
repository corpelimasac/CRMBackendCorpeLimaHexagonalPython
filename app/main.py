"""
FastAPI Application with Hexagonal Architecture
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys

from app.adapters.inbound.api.routers import health, generar_oc, dolar, upload_router, cotizacion_finalizada_router, proveedores_router, ordenes_compra, integracion_sunat
from app.config.settings import get_settings
from app.core.infrastructure.events.event_dispatcher import get_event_dispatcher

# Configurar logging
settings = get_settings()

logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle de la aplicación FastAPI

    Gestiona el inicio y cierre del EventDispatcher para eventos asíncronos
    """
    # Startup - Mostrar en consola directamente
    startup_msg = f"""
{'=' * 60}
🚀 Iniciando {settings.app_name}
📦 Versión: {settings.version}
🌍 Entorno: {settings.environment.upper()}
🐛 Debug: {settings.debug}
🗄️  Base de datos: {settings.database_url.split('@')[-1] if '@' in settings.database_url else settings.database_url}
{'=' * 60}
"""
    print(startup_msg)
    logger.info(startup_msg)

    event_dispatcher = get_event_dispatcher()
    workers_msg = f"✅ EventDispatcher inicializado con {event_dispatcher.executor._max_workers} workers"
    print(workers_msg)
    logger.info(workers_msg)

    yield

    # Shutdown
    shutdown_msg = f"""
{'=' * 60}
🛑 Apagando aplicación - Esperando eventos pendientes...
"""
    print(shutdown_msg)
    logger.info(shutdown_msg)

    event_dispatcher.shutdown(wait=True, timeout=settings.evento_financiero_timeout)

    final_msg = f"""
✅ Aplicación cerrada correctamente
{'=' * 60}
"""
    print(final_msg)
    logger.info(final_msg)


def create_app() -> FastAPI:
    """
    Crear y configurar la aplicación FastAPI
    """
    app = FastAPI(
        title="CRM Backend - Hexagonal Architecture",
        description="Sistema CRM implementado con arquitectura hexagonal",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan  # Configurar lifecycle
    )
    allowed_origins=settings.cors_origins.split(",")  if settings.cors_origins else [] 
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,  # En producción, especificar dominios exactos
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Registrar rutas
    app.include_router(health.router, prefix="/api", tags=["Health"])
    app.include_router(upload_router.router, prefix="/api", tags=["Generar Carta Garantia"])
    app.include_router(generar_oc.router, prefix="/api", tags=["Generar OC"])
    app.include_router(ordenes_compra.router, prefix="/api", tags=["Ordenes de Compra"])
    app.include_router(cotizacion_finalizada_router.router, prefix="/api", tags=["Cotizacion Finalizada"])
    app.include_router(dolar.router, prefix="/api", tags=["Dolar"])
    app.include_router(proveedores_router.router, prefix="/api", tags=["Proveedores"])
    app.include_router(integracion_sunat.router, prefix="/api", tags=["Integración con Sunat"])
    return app

# Crear la instancia de la aplicación
app = create_app()

@app.get("/") 
def read_root():
    return {"status": "API is running"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )