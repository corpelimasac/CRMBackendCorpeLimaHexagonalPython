from sqlalchemy import Column, Integer, Date, Numeric, String, ForeignKey, BIGINT
from sqlalchemy.orm import relationship
from .base import Base


class RegistroCompraOrdenModel(Base):
    """
    Modelo SQLAlchemy para la tabla de detalle de órdenes en registro de compras

    Almacena el detalle de cada orden de compra incluida en un registro de compra.
    Esta tabla funciona como registro histórico/detalle de las órdenes en el registro.
    """
    __tablename__ = "registro_compra_ordenes"

    orden_id = Column(BIGINT, primary_key=True, index=True, autoincrement=True)

    # Relación con registro de compra (Many-to-One)
    compra_id = Column(
        BIGINT,
        ForeignKey("registro_compras.compra_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Relación One-to-One con orden de compra
    id_orden = Column(
        Integer,
        ForeignKey("ordenes_compra.id_orden", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    # Datos de la orden
    fecha_orden_compra = Column(Date, nullable=False, comment="Fecha de esta orden de compra")
    moneda = Column(String(3), nullable=False, comment="PEN o USD")
    monto_total = Column(Numeric(12, 2), nullable=False, comment="Monto total de esta orden")

    # Relación Many-to-One con registro de compras
    registro_compra = relationship(
        "RegistroCompraModel",
        back_populates="registro_compra_ordenes"
    )

    # Relación One-to-One con orden de compra
    orden_compra = relationship(
        "OrdenesCompraModel",
        back_populates="registro_compra_orden"
    )
