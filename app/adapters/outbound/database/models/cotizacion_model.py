from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class CotizacionModel(Base):
  """
  Modelo SQLAlchemy para la tabla de cotizaciones
  
  """
  __tablename__ = "cotizacion"
  id_cotizacion = Column(Integer, primary_key=True, index=True, autoincrement=True,nullable=False)
  activo = Column(Boolean, default=True, nullable=True)
  fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
  fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
  igv=Column(Float, nullable=True)
  precio_venta=Column(Float, nullable=True)
  flete=Column(Float, nullable=True)
  id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
  total=Column(Float, nullable=True)
  referencia=Column(String(250), nullable=True)
