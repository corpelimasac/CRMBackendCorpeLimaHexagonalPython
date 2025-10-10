from sqlalchemy import Column, Date, Numeric, String, BIGINT
from sqlalchemy.orm import relationship
from .base import Base


class RegistroCompraModel(Base):
    """
    Modelo SQLAlchemy para la tabla de registro de compras consolidado

    Almacena el consolidado financiero de todas las órdenes de compra
    asociadas a una cotización específica.
    """
    __tablename__ = "registro_compras"

    compra_id = Column(BIGINT, primary_key=True, index=True, autoincrement=True)

    # Fecha de la orden de compra (fecha actual cuando se genera el registro)
    fecha_orden_compra = Column(Date, nullable=False, comment="Fecha cuando se generó el registro de compra")

    # Moneda
    moneda = Column(
        String(10),
        nullable=True,
        comment="Moneda predominante: SOLES, DOLARES, o MIXTO"
    )

    # Montos consolidados
    monto_total_dolar = Column(
        Numeric(12, 2),
        nullable=True,
        comment="Monto total consolidado en dólares"
    )
    tipo_cambio_sunat = Column(
        Numeric(6, 3),
        nullable=True,
        comment="Tipo de cambio SUNAT usado para conversión"
    )
    monto_total_soles = Column(
        Numeric(12, 2),
        nullable=False,
        comment="Monto total consolidado en soles"
    )
    monto_sin_igv = Column(
        Numeric(12, 2),
        nullable=False,
        comment="Monto sin IGV (18%)"
    )

    # Tipo de empresa
    tipo_empresa = Column(
        String(20),
        nullable=True,
        comment="CORPELIMA o CONSORCIO"
    )

    # Relaciones
    # Relación One-to-Many con registro_compra_ordenes
    registro_compra_ordenes = relationship(
        "RegistroCompraOrdenModel",
        back_populates="registro_compra",
        cascade="all, delete-orphan"
    )
