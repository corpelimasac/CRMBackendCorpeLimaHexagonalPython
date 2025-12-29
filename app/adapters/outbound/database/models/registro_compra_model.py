from sqlalchemy import Column, DateTime, Numeric, String, BIGINT, Boolean, ForeignKey
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

    # Relación con cotización versión
    cotizacion_version_id = Column(
        BIGINT,
        ForeignKey('cotizaciones_versiones.id_cotizacion_versiones'),
        nullable=True,
        index=True,
        comment="FK a la versión de cotización asociada"
    )

    # Campos de auditoría temporal
    fecha_creacion = Column(DateTime, nullable=False, comment="Fecha y hora de creación del registro", index=True)
    fecha_actualizacion = Column(DateTime, nullable=True, comment="Fecha y hora de la última actualización del registro")

    # Campo para marcar si el registro de compra ha sido modificado
    cambio_compra = Column(
        Boolean,
        nullable=False,
        server_default='0',
        comment="Indica si el registro de compra ha sido modificado (1) o no (0)"
    )

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

    # Estado del registro
    activo = Column(
        Boolean,
        nullable=False,
        server_default='1',
        comment="Indica si el registro está activo (1) o inactivo (0)"
    )

    # Campo para desactivación manual
    desactivado_manualmente = Column(
        Boolean,
        nullable=False,
        server_default='0',
        comment="Indica si el registro fue desactivado manualmente desde otro servicio"
    )

    # Relaciones
    # Relación One-to-Many con registro_compra_ordenes
    registro_compra_ordenes = relationship(
        "RegistroCompraOrdenModel",
        back_populates="registro_compra",
        cascade="all, delete-orphan"
    )
