from sqlalchemy import Column, String, DateTime, Text, BIGINT, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class OrdenesCompraAuditoriaModel(Base):
    """
    Modelo optimizado para auditar cambios en órdenes de compra.

    Registra todos los cambios (creación, actualización, eliminación)
    guardando solo IDs y obteniendo nombres mediante JOINs.
    Los cambios se almacenan en formato concatenado: "anterior ----> nuevo"
    """
    __tablename__ = "ordenes_compra_auditoria"

    id_auditoria = Column(BIGINT, primary_key=True, autoincrement=True, index=True)

    # Timestamp del cambio
    fecha_evento = Column(DateTime, nullable=False, default=datetime.now,
                         comment="Fecha y hora del cambio")

    # Tipo de operación
    tipo_operacion = Column(String(50), nullable=False,
                           comment="CREACION, ACTUALIZACION, ELIMINACION")

    # Referencias principales
    # Se permite NULL en id_orden_compra para mantener el historial cuando se elimina una orden
    id_orden_compra = Column(BIGINT, ForeignKey("ordenes_compra.id_orden", ondelete="SET NULL"),
                            nullable=True, index=True,
                            comment="ID de la orden de compra (NULL si fue eliminada)")

    # Número correlativo de la OC (se guarda directamente para mantener historial)
    numero_oc = Column(String(50), nullable=True,
                      comment="Número correlativo de la OC (ej: OC-000512-2025)")

    # Usuario que realizó el cambio
    id_usuario = Column(BIGINT, ForeignKey("usuarios.id_usuario"), nullable=False,
                       comment="ID del usuario que realizó el cambio")

    # Relaciones de la orden
    id_cotizacion = Column(BIGINT, ForeignKey("cotizacion.id_cotizacion"), nullable=True,
                          comment="ID de la cotización relacionada")

    id_cotizacion_versiones = Column(BIGINT, ForeignKey("cotizaciones_versiones.id_cotizacion_versiones"),
                                     nullable=True, comment="ID de la versión de cotización")

    # Cambios concatenados (formato: "id_anterior ----> id_nuevo" o solo "id" si es creación)
    cambio_proveedor = Column(String(255), nullable=True,
                             comment="Cambio de proveedor. Formato: 'id_anterior ----> id_nuevo' o solo 'id'")

    cambio_contacto = Column(String(255), nullable=True,
                            comment="Cambio de contacto. Formato: 'id_anterior ----> id_nuevo' o solo 'id'")

    cambio_monto = Column(String(100), nullable=True,
                         comment="Cambio de monto. Formato: 'monto_anterior ----> monto_nuevo' o solo 'monto'")

    # Productos (JSON con solo IDs)
    productos_agregados = Column(Text, nullable=True,
                                comment="Lista de IDs de productos agregados: [id1, id2, ...]")

    productos_modificados = Column(Text, nullable=True,
                                  comment="Cambios en productos: [{'id': X, 'cambios': {...}}]")

    productos_eliminados = Column(Text, nullable=True,
                                 comment="Lista de IDs de productos eliminados: [id1, id2, ...]")

    # Otros cambios (moneda, pago, entrega) en formato concatenado
    cambios_adicionales = Column(Text, nullable=True,
                                comment="Otros cambios en JSON. Formato: {'campo': 'anterior ----> nuevo'}")

    # Descripción legible del cambio
    descripcion = Column(Text, nullable=False,
                        comment="Descripción legible del cambio")

    # Relaciones (para obtener datos mediante JOIN)
    orden_compra = relationship("OrdenesCompraModel", foreign_keys=[id_orden_compra],
                               backref="auditorias")
    usuario = relationship("UsuariosModel", foreign_keys=[id_usuario],
                          backref="auditorias_ordenes_compra")
    cotizacion = relationship("CotizacionModel", foreign_keys=[id_cotizacion],
                             backref="auditorias_ordenes_compra")
    cotizacion_version = relationship("CotizacionesVersionesModel",
                                     foreign_keys=[id_cotizacion_versiones],
                                     backref="auditorias_ordenes_compra")

    def __repr__(self):
        return f"<OrdenesCompraAuditoria(id={self.id_auditoria}, tipo={self.tipo_operacion}, orden={self.id_orden_compra}, fecha={self.fecha_evento})>"
