from sqlalchemy import Column, Integer, BIGINT,  VARCHAR, BIT, Date, Enum, DECIMAL, ForeignKey
from datetime import datetime
from .base import Base

class DescuentoVendedorModel(Base):
  __tablename__ = "descuento_vendedor"
  id_descuento_vendedor = Column(BIGINT, primary_key=True, index=True, autoincrement=True, nullable=False)
  activo = Column(BIT, default=True, nullable=True)
  valor = Column(DECIMAL(38,2), nullable=True)
  fecha_creacion = Column(Date, default=datetime.now, nullable=True)
