from sqlalchemy import Column, Integer, VARCHAR, BIT, BIGINT, Date, Enum
from datetime import datetime
from .base import Base
from .intermedia_proveedor_contacto_model import intermedia_proveedor_contacto
from sqlalchemy.orm import relationship

class ProveedoresModel(Base):
  __tablename__ = "proveedores"
  id_proveedor = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
  condiciones_pago = Column(VARCHAR(255), nullable=True)
  departamento = Column(VARCHAR(255), nullable=True)
  direccion = Column(VARCHAR(255), nullable=True)
  distrito = Column(VARCHAR(255), nullable=True)
  estado = Column(BIT, default=True, nullable=True)
  fecha_actualizacion = Column(Date, default=datetime.now, nullable=True)
  fecha_registro = Column(Date, default=datetime.now, nullable=True)
  forma_entrega = Column(VARCHAR(255), nullable=True)
  observaciones = Column(VARCHAR(255), nullable=True)
  pais = Column(VARCHAR(255), nullable=True)
  provincia = Column(VARCHAR(255), nullable=True)
  razon_social = Column(VARCHAR(255), nullable=True)
  ruc = Column(BIGINT, nullable=True)
  tiempo_entrega = Column(VARCHAR(255), nullable=True)
  tipo_proveedor = Column(VARCHAR(255), nullable=True)
  web = Column(VARCHAR(255), nullable=True)
  nombre_comercial = Column(VARCHAR(255), nullable=True)
  nacional = Column(Enum('INTERNACIONAL','NACIONAL'), nullable=True)
  rubro = Column(VARCHAR(255), nullable=True)

  # Relación con la tabla de contactos
  contactos = relationship(
        "ContactoProveedorModel", secondary=intermedia_proveedor_contacto, back_populates="proveedores"
    )