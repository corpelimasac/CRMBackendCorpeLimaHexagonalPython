from sqlalchemy import Column, Integer, BIGINT,  VARCHAR, BIT
from .base import Base
from .intermedia_proveedor_contacto_model import intermedia_proveedor_contacto
from sqlalchemy.orm import relationship

class ContactoProveedorModel(Base):
  __tablename__ = "proveedor_contactos"
  id_proveedor_contacto = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
  celular=Column(BIGINT, nullable=True)
  correo=Column(VARCHAR(255), nullable=True)
  observacion=Column(VARCHAR(250), nullable=True)
  telefono=Column(VARCHAR(250), nullable=True)
  cargo=Column(VARCHAR(250), nullable=True)
  nombre=Column(VARCHAR(250), nullable=True)
  estado=Column(BIT, default=True, nullable=True)

  # Relación con la tabla de proveedores
  proveedores = relationship(
        "ProveedoresModel", secondary=intermedia_proveedor_contacto, back_populates="contactos"
    )

