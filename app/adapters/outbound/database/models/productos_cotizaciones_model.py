from sqlalchemy import Column, Integer, BIGINT,  VARCHAR, Boolean, Date, Enum, DECIMAL, ForeignKey
from datetime import datetime
from .base import Base



class ProductosCotizacionesModel(Base):
  __tablename__ = "productos_cotizaciones"
  id_producto_cotizacion = Column(BIGINT, primary_key=True, index=True, autoincrement=True, nullable=False)
  cantidad = Column(Integer, nullable=True)

  peso_total = Column(DECIMAL(38,2), nullable=True)
  producto_solicitado = Column(VARCHAR(255), nullable=True)
  diferencia = Column(DECIMAL(38,2), nullable=True)
  precio_costo_total_usd = Column(DECIMAL(38,2), nullable=True)
  tiempo_entrega = Column(VARCHAR(255), nullable=True)
  utilidad_proyectado = Column(DECIMAL(38,2), nullable=True)
  p_uni_usd = Column(DECIMAL(38,2), nullable=True)
  p_v_neto_usd = Column(DECIMAL(38,2), nullable=True)
  p_v_uni_usd = Column(DECIMAL(38,2), nullable=True)
  utilidad_real = Column(DECIMAL(38,2), nullable=True)
  utilidad_uni_real = Column(DECIMAL(38,2), nullable=True)
  utilidad_uni_proyectado = Column(DECIMAL(38,2), nullable=True)
  estado = Column(Boolean, default=True, nullable=True)
  fecha_creacion = Column(Date, default=datetime.now, nullable=True)
  fecha_modificacion = Column(Date, default=datetime.now, onupdate=datetime.now, nullable=True)

  p_lista_usd = Column(DECIMAL(38,2), nullable=True)

  # Relación con la tabla de productos
  id_producto = Column(Integer, ForeignKey("productos.id_producto"), nullable=True)

  # Relación con la tabla de cotizaciones versiones
  id_cotizacion_versiones = Column(BIGINT, ForeignKey("cotizaciones_versiones.id_cotizacion_versiones"), nullable=True)

  # Relación con la tabla de productos descuento
  id_producto_descuento = Column(BIGINT, ForeignKey("producto_descuento.id_producto_descuento"), nullable=True)

  # Relación con la tabla de productos descuento admin
  id_producto_descuento_admin = Column(BIGINT, ForeignKey("producto_descuento_admin.id_producto_descuento_admin"), nullable=True)