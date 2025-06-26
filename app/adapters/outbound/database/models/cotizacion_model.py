from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL, BIGINT, Date, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class CotizacionModel(Base):
  """
  Modelo SQLAlchemy para la tabla de cotizaciones
  
  """
  __tablename__ = "cotizacion"
  id_cotizacion = Column(BIGINT, primary_key=True, index=True, autoincrement=True,nullable=False)
  activo = Column(Boolean, default=True, nullable=True)
  fecha_creacion = Column(Date, default=datetime.now, nullable=True)
  fecha_actualizacion = Column(Date, default=datetime.now, onupdate=datetime.now, nullable=True)
  igv=Column(DECIMAL(38,2), nullable=True)
  precio_venta=Column(DECIMAL(38,2), nullable=True)
  flete=Column(DECIMAL(38,2), nullable=True)
  total=Column(DECIMAL(38,2), nullable=True)
  referencia=Column(String(250), nullable=True)

  # Relación con la tabla de usuarios
  id_usuario = Column(BIGINT, ForeignKey("usuarios.id_usuario"), nullable=False)
