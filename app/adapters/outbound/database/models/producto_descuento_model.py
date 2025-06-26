from sqlalchemy import Column, Integer, BIGINT,  Date, ForeignKey
from .base import Base

class ProductoDescuentoModel(Base):
  __tablename__ = "producto_descuento"
  id_producto_descuento = Column(BIGINT, primary_key=True, index=True, autoincrement=True, nullable=False)
  fecha_aplicacion = Column(Date, nullable=True)

  # Relación con la tabla de usuarios
  id_vendedor = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)

  # Relación con la tabla de descuento vendedor
  id_descuento_vendedor = Column(Integer, ForeignKey("descuento_vendedor.id_descuento_vendedor"), nullable=True)