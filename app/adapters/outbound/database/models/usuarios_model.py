from sqlalchemy import Column, Integer, String, DateTime, Boolean    
from datetime import datetime
from .base import Base

class UsuariosModel(Base):
  """
  Modelo SQLAlchemy para la tabla de usuarios
  
  Esta clase representa la tabla 'usuarios' en la base de datos.
  Mapea los campos de la entidad Usuario del dominio a columnas de la base de datos.
  """
  __tablename__ = "usuarios"
  id_usuario = Column(Integer, primary_key=True, index=True, autoincrement=True)
  username = Column(String(100), nullable=True, index=True)
  password = Column(String(100), nullable=False)
  nombre = Column(String(100), nullable=True)
  apellido = Column(String(100), nullable=True)
  correo = Column(String(100), nullable=False)
  celular = Column(Integer, nullable=True)
  estado = Column(Boolean, default=True, nullable=False)
  fecha_creacion = Column(DateTime, default=datetime.now, nullable=False)
  fecha_modificacion=Column(DateTime, default=datetime.now, onupdate=datetime.now)

  