"""
Configuración de la base de datos
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import Session
from typing import AsyncGenerator, Generator

from app.config.settings import get_settings

settings = get_settings()

# Base para los modelos SQLAlchemy
Base = declarative_base()

# Motor síncrono
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.debug
)

# Motor asíncrono
async_engine = create_async_engine(
    settings.async_database_url,
    echo=settings.debug
)

# Sesión síncrona
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Sesión asíncrona
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


def create_database():
    """Crear todas las tablas en la base de datos"""
    Base.metadata.create_all(bind=engine)


async def create_database_async():
    """Crear todas las tablas en la base de datos de forma asíncrona"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def get_db() ->Generator[Session, None, None]:
    """Dependencia para obtener una sesión de base de datos síncrona"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_db_async() -> AsyncGenerator[AsyncSession, None]:
    """Dependencia para obtener una sesión de base de datos asíncrona"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


class DatabaseManager:
    """Gestor de la base de datos"""
    
    def __init__(self):
        self.engine = engine
        self.async_engine = async_engine
    
    def create_tables(self):
        """Crear todas las tablas"""
        Base.metadata.create_all(bind=self.engine)
    
    async def create_tables_async(self):
        """Crear todas las tablas de forma asíncrona"""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def close(self):
        """Cerrar las conexiones de la base de datos"""
        await self.async_engine.dispose()


# Instancia global del gestor de base de datos
db_manager = DatabaseManager() 