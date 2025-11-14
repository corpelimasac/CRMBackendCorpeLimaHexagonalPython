from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
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
  correo = Column(String(100), nullable=False)
  estado = Column(Boolean, default=True, nullable=False)
  fecha_creacion = Column(Date, nullable=False)
  fecha_modificacion = Column(Date, nullable=True)
  comision_combinada_id = Column(Integer, nullable=True)
  comision_especial_id = Column(Integer, nullable=True)
  comision_vendedor_id = Column(Integer, nullable=True)
  id_trabajador = Column(Integer, ForeignKey('trabajadores.id_trabajador'), nullable=True, unique=True)

  # Relación con Trabajadores
  trabajador = relationship("TrabajadoresModel", foreign_keys=[id_trabajador])

  