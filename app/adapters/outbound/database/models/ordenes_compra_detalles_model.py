from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean, Date, BIGINT
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class OrdenesCompraDetallesModel(Base):
  """ 
  Modelo SQLAlchemy para la tabla de ordenes de compra detalles
  """
  __tablename__ = "ordenes_compra_detalles"
  id_oc_detalle = Column(Integer, primary_key=True, index=True, autoincrement=True)


  id_producto = Column(BIGINT, ForeignKey("productos.id_producto"), nullable=False)
  cantidad = Column(Integer, nullable=False)
  precio_unitario = Column(Float, nullable=False)
  precio_total = Column(Float, nullable=False)

  # Relación con la tabla de ordenes de compra
  id_orden = Column(BIGINT, ForeignKey("ordenes_compra.id_orden"), nullable=False)
