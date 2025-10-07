from sqlalchemy import Column, Integer, Date, Numeric
from .base import Base


class TasaCambioSunatModel(Base):
    """
    Modelo SQLAlchemy para la tabla de tasa de cambio SUNAT

    Esta tabla almacena los tipos de cambio oficiales de SUNAT
    """
    __tablename__ = "tasa_cambio_sunat"

    tasa_cambio_sunat_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    venta = Column(Numeric(8, 3), nullable=False, comment="Tipo de cambio venta")
    compra = Column(Numeric(8, 3), nullable=False, comment="Tipo de cambio compra")
    fecha = Column(Date, nullable=False, index=True, comment="Fecha del tipo de cambio")
