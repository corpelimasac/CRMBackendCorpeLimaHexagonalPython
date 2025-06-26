from sqlalchemy import Column, Integer, BIGINT,  VARCHAR, BIT, Date, Enum, DECIMAL, ForeignKey
from .base import Base

class ProveedorDetalleModel(Base):
  __tablename__ = "proveedor_detalle"
  id_proveedor_detalle = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
  igv = Column(VARCHAR(255), nullable=True)
  moneda = Column(VARCHAR(255), nullable=True)
  precio_costo_unitario = Column(DECIMAL(38,2), nullable=True)
  precio_costo_venta = Column(DECIMAL(38,2), nullable=True)

  # Relación con la tabla de productos
  id_producto = Column(Integer, ForeignKey("productos.id_producto"), nullable=True)

  # Relación con la tabla de proveedores
  id_proveedor = Column(Integer, ForeignKey("proveedores.id_proveedor"), nullable=True)