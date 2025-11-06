from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date, BIGINT, Numeric
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
  id_orden= Column(Integer, primary_key=True, index=True, autoincrement=True)
  correlative = Column(String(20), unique=True, nullable=False, index=True)
  ruta_s3 = Column(String(250), nullable=True)
  
  moneda=Column(String(255), nullable=True)
  total=Column(Numeric(12, 3), nullable=True)
  pago=Column(String(255), nullable=True)
  entrega=Column(String(255), nullable=True)
  consorcio=Column(Boolean, default=False, nullable=True)

  igv=Column(String(255), nullable=True)

  activo = Column(Boolean, default=True, nullable=True)
  fecha_creacion = Column(Date, default=datetime.now, nullable=True)

    # Relación con la tabla de cotizaciones versiones
  id_cotizacion_versiones = Column(BIGINT, ForeignKey("cotizaciones_versiones.id_cotizacion_versiones"), nullable=True)

    # Relación con la tabla de cotizaciones
  id_cotizacion = Column(BIGINT, ForeignKey("cotizacion.id_cotizacion"), nullable=False)

  # Relación con la tabla de usuarios
  id_usuario = Column(BIGINT, ForeignKey("usuarios.id_usuario"), nullable=False)

  # Relación de uno a uno con la tabla de proveedores
  id_proveedor = Column(BIGINT, ForeignKey("proveedores.id_proveedor"), nullable=False)

  # Relación de uno a uno con la tabla de proveedores contactos
  id_proveedor_contacto = Column(BIGINT, ForeignKey("proveedor_contactos.id_proveedor_contacto"), nullable=False)

  # Relación one-to-one con registro_compra_ordenes (la FK está en la otra tabla)
  registro_compra_orden = relationship(
      "RegistroCompraOrdenModel",
      back_populates="orden_compra",
      uselist=False
  )
