from sqlalchemy import Column, Integer, String, DateTime, Text, Numeric, BIGINT, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class RegistroCompraAuditoriaModel(Base):
    """
    Modelo para auditar cambios en registro de compras.

    Registra todos los cambios (creación, actualización, eliminación)
    en los registros de compra y sus órdenes asociadas.
    """
    __tablename__ = "registro_compra_auditoria"

    id_auditoria = Column(BIGINT, primary_key=True, autoincrement=True, index=True)

    # Timestamp del cambio
    fecha_evento = Column(DateTime, nullable=False, default=datetime.now,
                         comment="Fecha y hora del cambio")

    # Tipo de operación
    tipo_operacion = Column(String(50), nullable=False,
                           comment="CREACION, ACTUALIZACION, ELIMINACION")

    # Tipo de entidad afectada
    tipo_entidad = Column(String(50), nullable=False,
                         comment="REGISTRO_COMPRA, ORDEN_COMPRA, REGISTRO_COMPRA_ORDEN")

    # IDs de las entidades involucradas
    # NOTA: compra_id NO tiene FK porque es una tabla de auditoría histórica.
    # El registro de compra puede ser eliminado pero la auditoría debe conservarse.
    # El compra_id se mantiene como referencia histórica.

    id_cotizacion = Column(BIGINT, ForeignKey("cotizacion.id_cotizacion"), nullable=True, index=True,
                          comment="ID de la cotización")

    id_cotizacion_versiones = Column(BIGINT, ForeignKey("cotizaciones_versiones.id_cotizacion_versiones"), nullable=True,
                                     comment="ID de la versión de cotización")

    # Usuario que realizó el cambio (si está disponible)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True,
                       comment="ID del usuario que realizó el cambio")

    # Relaciones
    cotizacion = relationship("CotizacionModel", foreign_keys="[RegistroCompraAuditoriaModel.id_cotizacion]", backref="auditorias_compra")
    cotizacion_version = relationship("CotizacionesVersionesModel", foreign_keys="[RegistroCompraAuditoriaModel.id_cotizacion_versiones]", backref="auditorias_compra")
    usuario = relationship("UsuariosModel", foreign_keys="[RegistroCompraAuditoriaModel.id_usuario]", backref="auditorias_compra")

    # Datos antes del cambio (JSON)
    datos_anteriores = Column(Text, nullable=True,
                             comment="Estado anterior en formato JSON")

    # Datos después del cambio (JSON)
    datos_nuevos = Column(Text, nullable=True,
                         comment="Estado nuevo en formato JSON")

    # Montos para consultas rápidas
    monto_anterior = Column(Numeric(12, 2), nullable=True,
                           comment="Monto total anterior")

    monto_nuevo = Column(Numeric(12, 2), nullable=True,
                        comment="Monto total nuevo")

    # Descripción del cambio
    descripcion = Column(Text, nullable=False,
                        comment="Descripción legible del cambio")

    # Razón del cambio (opcional)
    razon = Column(Text, nullable=True,
                  comment="Razón del cambio (si se proporciona)")

    # Metadata adicional
    metadata_json = Column(Text, nullable=True,
                          comment="Información adicional en JSON")

    def __repr__(self):
        return f"<RegistroCompraAuditoria(id={self.id_auditoria}, tipo={self.tipo_operacion}, fecha={self.fecha_evento})>"
