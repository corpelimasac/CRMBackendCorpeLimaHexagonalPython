"""
Configuración de la base de datos
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from typing import Generator

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

# Sesión síncrona
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_database():
    """Crear todas las tablas en la base de datos"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependencia para obtener una sesión de base de datos síncrona"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseManager:
    """Gestor de la base de datos"""
    
    def __init__(self):
        self.engine = engine
    
    def create_tables(self):
        """Crear todas las tablas"""
        Base.metadata.create_all(bind=self.engine)


# Instancia global del gestor de base de datos
db_manager = DatabaseManager() 