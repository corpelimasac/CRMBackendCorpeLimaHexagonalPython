"""
Servicio de auditoría para registros de compra.

Este servicio registra todos los cambios (creación, actualización, eliminación)
en los registros de compra para mantener un historial completo de auditoría.
"""
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.adapters.outbound.database.models.registro_compra_auditoria_model import RegistroCompraAuditoriaModel
from app.adapters.outbound.database.models.ordenes_compra_model import OrdenesCompraModel

logger = logging.getLogger(__name__)


class RegistroCompraAuditoriaService:
    """
    Servicio para registrar cambios en registros de compra.
    """

    def __init__(self, db: Session):
        self.db = db

    def registrar_creacion_registro(
        self,
        compra_id: int,
        id_cotizacion: int,
        id_cotizacion_versiones: int,
        datos_nuevos: Dict[str, Any],
        ordenes: List[OrdenesCompraModel],
        id_usuario: Optional[int] = None
    ) -> None:
        """
        Registra la creación de un nuevo registro de compra.

        IMPORTANTE: Este método NO hace commit. El commit debe ser manejado
        por el repositorio que lo llama para mantener integridad transaccional.

        Args:
            compra_id: ID del registro de compra creado
            id_cotizacion: ID de la cotización
            id_cotizacion_versiones: ID de la versión
            datos_nuevos: Datos del registro creado
            ordenes: Lista de órdenes incluidas
            id_usuario: ID del usuario (opcional)
        """
        try:
            monto_nuevo = float(datos_nuevos.get('monto_total_soles', 0))
            cantidad_ordenes = len(ordenes)

            descripcion = (
                f"Registro de compra creado para cotización {id_cotizacion} versión {id_cotizacion_versiones}. "
                f"Total: S/ {monto_nuevo:,.2f}. "
                f"Órdenes incluidas: {cantidad_ordenes}"
            )

            auditoria = RegistroCompraAuditoriaModel(
                fecha_evento=datetime.now(),
                tipo_operacion="CREACION",
                tipo_entidad="REGISTRO_COMPRA",
                id_cotizacion=id_cotizacion,
                id_cotizacion_versiones=id_cotizacion_versiones,
                id_usuario=id_usuario,
                datos_nuevos=json.dumps(datos_nuevos, default=str),
                monto_nuevo=monto_nuevo,
                descripcion=descripcion,
                metadata_json=json.dumps({
                    'cantidad_ordenes': cantidad_ordenes,
                    'ordenes_ids': [o.id_orden for o in ordenes]
                })
            )

            self.db.add(auditoria)
            # NO hacer commit aquí - dejar que el repositorio haga commit de toda la transacción
            logger.info(f"Auditoria registrada (pendiente commit): Creacion de registro {compra_id}")

        except Exception as e:
            logger.error(f"Error al registrar auditoria de creacion: {e}", exc_info=True)
            # Re-lanzar la excepción para que el repositorio haga rollback de toda la transacción
            raise

    def registrar_actualizacion_registro(
        self,
        compra_id: int,
        id_cotizacion: int,
        id_cotizacion_versiones: int,
        datos_anteriores: Dict[str, Any],
        datos_nuevos: Dict[str, Any],
        ordenes_anteriores: List[OrdenesCompraModel],
        ordenes_nuevas: List[OrdenesCompraModel],
        id_usuario: Optional[int] = None
    ) -> None:
        """
        Registra la actualización de un registro de compra.

        IMPORTANTE: Este método NO hace commit. El commit debe ser manejado
        por el repositorio que lo llama para mantener integridad transaccional.

        Args:
            compra_id: ID del registro actualizado
            id_cotizacion: ID de la cotización
            id_cotizacion_versiones: ID de la versión
            datos_anteriores: Datos antes de la actualización
            datos_nuevos: Datos después de la actualización
            ordenes_anteriores: Órdenes antes del cambio
            ordenes_nuevas: Órdenes después del cambio
            id_usuario: ID del usuario (opcional)
        """
        try:
            monto_anterior = float(datos_anteriores.get('monto_total_soles', 0))
            monto_nuevo = float(datos_nuevos.get('monto_total_soles', 0))
            diferencia = monto_nuevo - monto_anterior

            cant_ordenes_anterior = len(ordenes_anteriores)
            cant_ordenes_nueva = len(ordenes_nuevas)

            # Determinar qué cambió
            cambios = []
            if monto_anterior != monto_nuevo:
                signo = "+" if diferencia > 0 else ""
                cambios.append(f"Total: S/ {monto_anterior:,.2f} → S/ {monto_nuevo:,.2f} ({signo}S/ {diferencia:,.2f})")

            if cant_ordenes_anterior != cant_ordenes_nueva:
                cambios.append(f"Órdenes: {cant_ordenes_anterior} → {cant_ordenes_nueva}")

            descripcion = (
                f"Registro de compra {compra_id} actualizado. "
                f"{'. '.join(cambios)}"
            )

            auditoria = RegistroCompraAuditoriaModel(
                fecha_evento=datetime.now(),
                tipo_operacion="ACTUALIZACION",
                tipo_entidad="REGISTRO_COMPRA",
                id_cotizacion=id_cotizacion,
                id_cotizacion_versiones=id_cotizacion_versiones,
                id_usuario=id_usuario,
                datos_anteriores=json.dumps(datos_anteriores, default=str),
                datos_nuevos=json.dumps(datos_nuevos, default=str),
                monto_anterior=monto_anterior,
                monto_nuevo=monto_nuevo,
                descripcion=descripcion,
                metadata_json=json.dumps({
                    'cantidad_ordenes_anterior': cant_ordenes_anterior,
                    'cantidad_ordenes_nueva': cant_ordenes_nueva,
                    'ordenes_ids_anteriores': [o.id_orden for o in ordenes_anteriores],
                    'ordenes_ids_nuevas': [o.id_orden for o in ordenes_nuevas],
                    'diferencia_monto': float(diferencia)
                })
            )

            self.db.add(auditoria)
            # NO hacer commit aquí - dejar que el repositorio haga commit de toda la transacción
            logger.info(f"Auditoria registrada (pendiente commit): Actualizacion de registro {compra_id}")

        except Exception as e:
            logger.error(f"Error al registrar auditoria de actualizacion: {e}", exc_info=True)
            # Re-lanzar la excepción para que el repositorio haga rollback de toda la transacción
            raise

    def registrar_desactivacion_registro(
        self,
        compra_id: int,
        id_cotizacion: int,
        id_cotizacion_versiones: int,
        datos_anteriores: Dict[str, Any],
        ordenes: List[OrdenesCompraModel],
        razon: str,
        id_usuario: Optional[int] = None
    ) -> None:
        """
        Registra la desactivación de un registro de compra.

        IMPORTANTE: Este método NO hace commit. El commit debe ser manejado
        por el repositorio que lo llama para mantener integridad transaccional.

        Args:
            compra_id: ID del registro desactivado
            id_cotizacion: ID de la cotización
            id_cotizacion_versiones: ID de la versión
            datos_anteriores: Datos antes de desactivar (dict completo con toda la info)
            ordenes: Órdenes que tenía el registro
            razon: Razón de la desactivación
            id_usuario: ID del usuario (opcional)
        """
        try:
            monto_anterior = float(datos_anteriores.get('monto_total_soles', 0))
            cantidad_ordenes = len(ordenes)

            descripcion = (
                f"Registro de compra {compra_id} marcado como inactivo. "
                f"Total del registro: S/ {monto_anterior:,.2f}. "
                f"Cantidad de órdenes asociadas: {cantidad_ordenes}. "
                f"Razón: {razon}"
            )

            auditoria = RegistroCompraAuditoriaModel(
                fecha_evento=datetime.now(),
                tipo_operacion="DESACTIVACION",
                tipo_entidad="REGISTRO_COMPRA",
                id_cotizacion=id_cotizacion,
                id_cotizacion_versiones=id_cotizacion_versiones,
                id_usuario=id_usuario,
                datos_anteriores=json.dumps(datos_anteriores, default=str),
                monto_anterior=monto_anterior,
                descripcion=descripcion,
                razon=razon,
                metadata_json=json.dumps({
                    'cantidad_ordenes': cantidad_ordenes,
                    'ordenes_ids': [o.id_orden for o in ordenes],
                    'accion': 'desactivacion'
                })
            )

            self.db.add(auditoria)
            # NO hacer commit aquí - dejar que el repositorio haga commit de toda la transacción
            logger.info(f"Auditoria registrada (pendiente commit): Desactivacion de registro {compra_id}")

        except Exception as e:
            logger.error(f"Error al registrar auditoria de desactivacion de registro: {e}", exc_info=True)
            # Re-lanzar la excepción para que el repositorio haga rollback de toda la transacción
            raise

    def registrar_eliminacion_registro(
        self,
        compra_id: int,
        id_cotizacion: int,
        id_cotizacion_versiones: int,
        datos_anteriores: Dict[str, Any],
        ordenes: List[OrdenesCompraModel],
        razon: str,
        id_usuario: Optional[int] = None
    ) -> None:
        """
        Registra la eliminación de un registro de compra.

        IMPORTANTE: Este método NO hace commit. El commit debe ser manejado
        por el repositorio que lo llama para mantener integridad transaccional.

        Args:
            compra_id: ID del registro eliminado
            id_cotizacion: ID de la cotización
            id_cotizacion_versiones: ID de la versión
            datos_anteriores: Datos antes de eliminar (dict completo con toda la info)
            ordenes: Órdenes que tenía el registro
            razon: Razón de la eliminación
            id_usuario: ID del usuario (opcional)
        """
        try:
            monto_anterior = float(datos_anteriores.get('monto_total_soles', 0))
            cantidad_ordenes = len(ordenes)

            descripcion = (
                f"Registro de compra {compra_id} eliminado completamente. "
                f"Total eliminado: S/ {monto_anterior:,.2f}. "
                f"Cantidad de órdenes asociadas: {cantidad_ordenes}. "
                f"Razón: {razon}"
            )

            auditoria = RegistroCompraAuditoriaModel(
                fecha_evento=datetime.now(),
                tipo_operacion="ELIMINACION",
                tipo_entidad="REGISTRO_COMPRA",
                id_cotizacion=id_cotizacion,
                id_cotizacion_versiones=id_cotizacion_versiones,
                id_usuario=id_usuario,
                datos_anteriores=json.dumps(datos_anteriores, default=str),
                monto_anterior=monto_anterior,
                descripcion=descripcion,
                razon=razon,
                metadata_json=json.dumps({
                    'cantidad_ordenes': cantidad_ordenes,
                    'ordenes_ids': [o.id_orden for o in ordenes]
                })
            )

            self.db.add(auditoria)
            # NO hacer commit aquí - dejar que el repositorio haga commit de toda la transacción
            logger.info(f"Auditoria registrada (pendiente commit): Eliminacion de registro {compra_id}")

        except Exception as e:
            logger.error(f"Error al registrar auditoria de eliminacion de registro: {e}", exc_info=True)
            # Re-lanzar la excepción para que el repositorio haga rollback de toda la transacción
            raise

    def registrar_eliminacion_orden(
        self,
        id_orden: int,
        numero_oc: str,
        id_cotizacion: int,
        id_cotizacion_versiones: int,
        monto_orden: float,
        tenia_registro: bool,
        compra_id: Optional[int] = None,
        id_usuario: Optional[int] = None
    ) -> None:
        """
        Registra la eliminación de una orden de compra.

        Args:
            id_orden: ID de la orden eliminada
            numero_oc: Número de OC
            id_cotizacion: ID de la cotización
            id_cotizacion_versiones: ID de la versión
            monto_orden: Monto de la orden
            tenia_registro: Si la orden estaba en un registro de compra
            compra_id: ID del registro (si lo tenía)
            id_usuario: ID del usuario (opcional)
        """
        try:
            if tenia_registro:
                descripcion = (
                    f"Orden de compra {numero_oc} (ID: {id_orden}) eliminada. "
                    f"Estaba en registro de compra {compra_id}. "
                    f"Monto: S/ {monto_orden:,.2f}. "
                    f"El registro de compra será recalculado automáticamente."
                )
            else:
                descripcion = (
                    f"Orden de compra {numero_oc} (ID: {id_orden}) eliminada. "
                    f"No estaba asociada a ningún registro de compra. "
                    f"Monto: S/ {monto_orden:,.2f}"
                )

            auditoria = RegistroCompraAuditoriaModel(
                fecha_evento=datetime.now(),
                tipo_operacion="ELIMINACION",
                tipo_entidad="ORDEN_COMPRA",
                id_cotizacion=id_cotizacion,
                id_cotizacion_versiones=id_cotizacion_versiones,
                id_usuario=id_usuario,
                datos_anteriores=json.dumps({
                    'numero_oc': numero_oc,
                    'id_orden': id_orden,  # Guardar el ID en los datos para referencia
                    'compra_id': compra_id,  # Guardar el compra_id en los datos para referencia
                    'monto': float(monto_orden),
                    'tenia_registro': tenia_registro
                }),
                monto_anterior=float(monto_orden),
                descripcion=descripcion,
                razon="Eliminación de orden de compra"
            )

            self.db.add(auditoria)
            # NO hacer commit aquí - dejar que el repositorio haga commit de toda la transacción
            logger.info(f"Auditoria registrada (pendiente commit): Eliminacion de orden {numero_oc}")

        except Exception as e:
            logger.error(f"Error al registrar auditoria de eliminacion de orden: {e}", exc_info=True)
            # Re-lanzar la excepción para que el repositorio haga rollback de toda la transacción
            raise

    def registrar_actualizacion_orden(
        self,
        id_orden: int,
        numero_oc: str,
        id_cotizacion: int,
        id_cotizacion_versiones: int,
        monto_anterior: float,
        monto_nuevo: float,
        cambios_detalle: str,
        compra_id: Optional[int] = None,
        id_usuario: Optional[int] = None
    ) -> None:
        """
        Registra la actualización de una orden de compra.

        Args:
            id_orden: ID de la orden actualizada
            numero_oc: Número de OC
            id_cotizacion: ID de la cotización
            id_cotizacion_versiones: ID de la versión
            monto_anterior: Monto antes del cambio
            monto_nuevo: Monto después del cambio
            cambios_detalle: Descripción de los cambios
            compra_id: ID del registro (si lo tiene)
            id_usuario: ID del usuario (opcional)
        """
        try:
            diferencia = monto_nuevo - monto_anterior
            signo = "+" if diferencia > 0 else ""

            descripcion = (
                f"Orden de compra {numero_oc} (ID: {id_orden}) actualizada. "
                f"Monto: S/ {monto_anterior:,.2f} → S/ {monto_nuevo:,.2f} ({signo}S/ {diferencia:,.2f}). "
                f"Cambios: {cambios_detalle}"
            )

            if compra_id:
                descripcion += f" El registro de compra {compra_id} será recalculado."

            auditoria = RegistroCompraAuditoriaModel(
                fecha_evento=datetime.now(),
                tipo_operacion="ACTUALIZACION",
                tipo_entidad="ORDEN_COMPRA",
                id_cotizacion=id_cotizacion,
                id_cotizacion_versiones=id_cotizacion_versiones,
                id_usuario=id_usuario,
                datos_anteriores=json.dumps({
                    'id_orden': id_orden,
                    'compra_id': compra_id,
                    'monto': float(monto_anterior)
                }),
                datos_nuevos=json.dumps({
                    'id_orden': id_orden,
                    'compra_id': compra_id,
                    'monto': float(monto_nuevo)
                }),
                monto_anterior=float(monto_anterior),
                monto_nuevo=float(monto_nuevo),
                descripcion=descripcion,
                razon="Actualización de orden de compra",
                metadata_json=json.dumps({
                    'cambios_detalle': cambios_detalle,
                    'diferencia_monto': float(diferencia)
                })
            )

            self.db.add(auditoria)
            # NO hacer commit aquí - dejar que el caso de uso haga commit de toda la transacción
            logger.info(f"Auditoria registrada (pendiente commit): Actualizacion de orden {numero_oc}")

        except Exception as e:
            logger.error(f"Error al registrar auditoria de actualizacion de orden: {e}", exc_info=True)
            # Re-lanzar la excepción para que haya rollback completo
            raise
