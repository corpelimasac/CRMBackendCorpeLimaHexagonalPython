from sqlalchemy import Column, Integer, String, DateTime, Text, Numeric, BIGINT, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class OrdenesCompraAuditoriaModel(Base):
    """
    Modelo para auditar cambios en órdenes de compra.

    Registra todos los cambios (creación, actualización, eliminación)
    en las órdenes de compra, incluyendo:
    - Cambios en proveedor
    - Cambios en contacto
    - Productos agregados, modificados y eliminados
    """
    __tablename__ = "ordenes_compra_auditoria"

    id_auditoria = Column(BIGINT, primary_key=True, autoincrement=True, index=True)

    # Timestamp del cambio
    fecha_evento = Column(DateTime, nullable=False, default=datetime.now,
                         comment="Fecha y hora del cambio")

    # Tipo de operación
    tipo_operacion = Column(String(50), nullable=False,
                           comment="CREACION, ACTUALIZACION, ELIMINACION")

    # Referencias de la orden de compra
    id_orden_compra = Column(BIGINT, nullable=False, index=True,
                            comment="ID de la orden de compra")

    numero_oc = Column(String(20), nullable=False, index=True,
                      comment="Número correlativo de la OC")

    # Usuario que realizó el cambio
    id_usuario = Column(BIGINT, ForeignKey("usuarios.id_usuario"), nullable=False,
                       comment="ID del usuario que realizó el cambio")

    # Relaciones de la orden
    id_cotizacion = Column(BIGINT, ForeignKey("cotizacion.id_cotizacion"), nullable=True,
                          comment="ID de la cotización relacionada")

    id_cotizacion_versiones = Column(BIGINT, ForeignKey("cotizaciones_versiones.id_cotizacion_versiones"),
                                     nullable=True, comment="ID de la versión de cotización")

    # Cambios de proveedor (registrar antiguo -> nuevo)
    id_proveedor_anterior = Column(BIGINT, nullable=True,
                                   comment="ID del proveedor anterior")

    proveedor_anterior = Column(String(255), nullable=True,
                               comment="Razón social del proveedor anterior")

    id_proveedor_nuevo = Column(BIGINT, nullable=True,
                                comment="ID del proveedor nuevo")

    proveedor_nuevo = Column(String(255), nullable=True,
                            comment="Razón social del proveedor nuevo")

    # Cambios de contacto (registrar antiguo -> nuevo)
    id_contacto_anterior = Column(BIGINT, nullable=True,
                                  comment="ID del contacto anterior")

    contacto_anterior = Column(String(255), nullable=True,
                              comment="Nombre del contacto anterior")

    id_contacto_nuevo = Column(BIGINT, nullable=True,
                               comment="ID del contacto nuevo")

    contacto_nuevo = Column(String(255), nullable=True,
                           comment="Nombre del contacto nuevo")

    # Cambios en productos (formato JSON)
    productos_agregados = Column(Text, nullable=True,
                                comment="Productos agregados en formato JSON")

    productos_modificados = Column(Text, nullable=True,
                                  comment="Productos modificados en formato JSON")

    productos_eliminados = Column(Text, nullable=True,
                                 comment="Productos eliminados en formato JSON")

    # Montos para consultas rápidas
    monto_anterior = Column(Numeric(12, 2), nullable=True,
                           comment="Monto total anterior")

    monto_nuevo = Column(Numeric(12, 2), nullable=True,
                        comment="Monto total nuevo")

    # Otros cambios
    cambios_adicionales = Column(Text, nullable=True,
                                comment="Otros cambios (moneda, pago, entrega) en JSON")

    # Descripción legible del cambio
    descripcion = Column(Text, nullable=False,
                        comment="Descripción legible del cambio")

    # Razón del cambio (opcional)
    razon = Column(Text, nullable=True,
                  comment="Razón del cambio (si se proporciona)")

    # Metadata adicional
    metadata_json = Column(Text, nullable=True,
                          comment="Información adicional en JSON")

    # Relaciones
    usuario = relationship("UsuariosModel", foreign_keys=[id_usuario], backref="auditorias_ordenes_compra")
    cotizacion = relationship("CotizacionModel", foreign_keys=[id_cotizacion], backref="auditorias_ordenes_compra")
    cotizacion_version = relationship("CotizacionesVersionesModel",
                                     foreign_keys=[id_cotizacion_versiones],
                                     backref="auditorias_ordenes_compra")

    def __repr__(self):
        return f"<OrdenesCompraAuditoria(id={self.id_auditoria}, tipo={self.tipo_operacion}, oc={self.numero_oc}, fecha={self.fecha_evento})>"
