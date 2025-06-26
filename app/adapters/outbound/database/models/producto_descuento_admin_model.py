from sqlalchemy import Column, Integer, BIGINT,  Date, DECIMAL, ForeignKey
from .base import Base

class ProductoDescuentoAdminModel(Base):
  __tablename__ = "producto_descuento_admin"
  id_producto_descuento_admin = Column(BIGINT, primary_key=True, index=True, autoincrement=True, nullable=False)
  descuento_admin = Column(DECIMAL(38,2), nullable=True)
  fecha_aplicacion = Column(Date, nullable=True)

  # Relación con la tabla de usuarios admin
  id_admin = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)