"""
FastAPI Application with Hexagonal Architecture
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys

from app.adapters.inbound.api.routers import health, dolar, upload_router, cotizacion_finalizada_router, proveedores_router, ordenes_compra, integracion_sunat
from app.config.settings import get_settings
from app.core.infrastructure.events.event_dispatcher import get_event_dispatcher

# Configurar logging
settings = get_settings()

logging.basicConfig(
    level=logging.DEBUG,  # Siempre DEBUG para ver todos los errores
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ],
    force=True  # Forzar reconfiguración
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

    event_dispatcher.shutdown(wait=True)

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
    # Middleware para loggear TODOS los requests
    @app.middleware("http")
    async def log_requests(request, call_next):
        import time
        import traceback

        start_time = time.time()
        print(f"\n→ REQUEST: {request.method} {request.url.path}")

        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            print(f"← RESPONSE: {response.status_code} ({process_time:.2f}s)")
            return response
        except Exception as e:
            process_time = time.time() - start_time
            print(f"\n!!! EXCEPCION EN MIDDLEWARE ({process_time:.2f}s):")
            print(f"Path: {request.url.path}")
            print(f"Error: {str(e)}")
            print(f"Tipo: {type(e).__name__}")
            traceback.print_exc()
            raise

    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,  # En producción, especificar dominios exactos
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Middleware para capturar excepciones NO HTTP
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        # No capturar excepciones HTTP (como 405 Method Not Allowed)
        from fastapi.exceptions import HTTPException
        from starlette.exceptions import HTTPException as StarletteHTTPException

        if isinstance(exc, (HTTPException, StarletteHTTPException)):
            # Dejar que FastAPI maneje estos errores
            raise exc

        # Capturar otros errores
        import traceback
        error_trace = traceback.format_exc()
        print(f"\n[EXCEPTION HANDLER] ERROR:")
        print(f"Path: {request.url.path}")
        print(f"Error: {str(exc)}")
        print(f"Traceback:\n{error_trace}")
        logger.error(f"Error en {request.url.path}: {str(exc)}\n{error_trace}")

        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "path": request.url.path, "type": type(exc).__name__}
        )

    # Registrar rutas
    app.include_router(health.router, prefix="/api", tags=["Health"])
    app.include_router(upload_router.router, prefix="/api", tags=["Generar Carta Garantia"])
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