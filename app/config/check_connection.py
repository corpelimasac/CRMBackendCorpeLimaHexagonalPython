from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from app.config.settings import get_settings

# Obtener los ajustes de la configuración
settings = get_settings()

# Crear un motor de base de datos
DATABASE_URL = settings.database_url  # Usamos la URL de conexión configurada
engine = create_engine(DATABASE_URL, echo=True)

# Crear una sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_database_connection():
    try:
        # Intenta conectar a la base de datos ejecutando una consulta simple
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))  # Consulta simple para verificar la conexión
        return True
    except OperationalError as e:
        print(f"Error de conexión a la base de datos: {e}")
        return False