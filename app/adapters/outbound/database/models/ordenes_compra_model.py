from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class OrdenesCompraModel(Base):
  """ 
  Modelo SQLAlchemy para la tabla de ordenes de compra
  
  Esta clase representa la tabla 'ordenes_compra' en la base de datos.
  Mapea los campos de la entidad OrdenesCompra del dominio a columnas de la base de datos.
  """
  __tablename__ = "ordenes_compra"
  id_orden = Column(Integer, primary_key=True, index=True, autoincrement=True)
  id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)

  fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
  fecha_modificacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)