"""
Servicio optimizado de auditoría para órdenes de compra.

Este servicio registra cambios guardando solo IDs y concatenando valores
en formato "anterior ----> nuevo". Los nombres se obtienen mediante JOINs.
"""
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.adapters.outbound.database.models.ordenes_compra_auditoria_model import OrdenesCompraAuditoriaModel

logger = logging.getLogger(__name__)


class OrdenesCompraAuditoriaService:
    """
    Servicio para registrar cambios en órdenes de compra con formato optimizado.

    Formato de datos:
    - IDs sin nombres (nombres se obtienen por JOIN)
    - Cambios concatenados: "anterior ----> nuevo"
    - Productos solo como IDs
    """

    def __init__(self, db: Session):
        self.db = db

    def registrar_creacion_orden(
        self,
        id_orden_compra: int,
        id_usuario: int,
        id_cotizacion: int,
        id_cotizacion_versiones: int,
        id_proveedor: int,
        id_contacto: int,
        productos: List[Dict[str, Any]],  # productos con id_producto
        monto_total: float,
        otros_datos: Optional[Dict[str, Any]] = None,
        numero_oc: str = None
    ) -> None:
        """
        Registra la creación de una nueva orden de compra.

        Args:
            id_orden_compra: ID de la orden creada
            id_usuario: ID del usuario que creó la orden
            id_cotizacion: ID de la cotización
            id_cotizacion_versiones: ID de la versión de cotización
            id_proveedor: ID del proveedor
            id_contacto: ID del contacto
            productos: Lista de productos con id_producto
            monto_total: Monto total de la orden
            otros_datos: Otros datos (moneda, pago, entrega)
            numero_oc: Número correlativo de la OC (ej: OC-000512-2025)
        """
        try:
            cantidad_productos = len(productos)

            descripcion = (
                f"Orden de compra creada con {cantidad_productos} producto(s). "
                f"Monto total: S/ {monto_total:,.2f}"
            )

            # Solo guardar IDs de productos agregados
            ids_productos = [str(p.get('id_producto')) for p in productos]
            productos_agregados_json = json.dumps(ids_productos) if ids_productos else None

            # Preparar cambios adicionales si existen
            cambios_adicionales_json = None
            if otros_datos:
                cambios_adicionales_json = json.dumps(otros_datos)

            # Crear registro de auditoría
            auditoria = OrdenesCompraAuditoriaModel(
                tipo_operacion="CREACION",
                fecha_evento=datetime.now(),
                id_orden_compra=id_orden_compra,
                numero_oc=numero_oc,  # Guardar número de OC
                id_usuario=id_usuario,
                id_cotizacion=id_cotizacion,
                id_cotizacion_versiones=id_cotizacion_versiones,
                # Solo IDs, sin flechas para creación
                cambio_proveedor=str(id_proveedor),
                cambio_contacto=str(id_contacto),
                cambio_monto=str(monto_total),
                productos_agregados=productos_agregados_json,
                cambios_adicionales=cambios_adicionales_json,
                descripcion=descripcion
            )

            self.db.add(auditoria)
            logger.info(f"✅ Auditoría de creación registrada para orden {id_orden_compra}")

        except Exception as e:
            logger.error(f"❌ Error al registrar auditoría de creación: {e}", exc_info=True)
            raise

    def registrar_actualizacion_orden(
        self,
        id_orden_compra: int,
        id_usuario: int,
        id_cotizacion: int,
        id_cotizacion_versiones: int,
        # Proveedor (solo si cambió)
        id_proveedor_anterior: Optional[int] = None,
        id_proveedor_nuevo: Optional[int] = None,
        # Contacto (solo si cambió)
        id_contacto_anterior: Optional[int] = None,
        id_contacto_nuevo: Optional[int] = None,
        # Productos
        productos_agregados: Optional[List[Dict[str, Any]]] = None,
        productos_modificados: Optional[List[Dict[str, Any]]] = None,
        productos_eliminados: Optional[List[Dict[str, Any]]] = None,
        # Montos
        monto_anterior: Optional[float] = None,
        monto_nuevo: Optional[float] = None,
        # Otros cambios
        otros_cambios: Optional[Dict[str, Dict[str, Any]]] = None,
        numero_oc: str = None
    ) -> None:
        """
        Registra la actualización de una orden de compra.

        Args:
            id_orden_compra: ID de la orden actualizada
            id_usuario: ID del usuario que realizó la actualización
            id_cotizacion: ID de la cotización
            id_cotizacion_versiones: ID de la versión de cotización
            id_proveedor_anterior: ID del proveedor anterior (si cambió)
            id_proveedor_nuevo: ID del proveedor nuevo (si cambió)
            id_contacto_anterior: ID del contacto anterior (si cambió)
            id_contacto_nuevo: ID del contacto nuevo (si cambió)
            productos_agregados: Lista de productos agregados con id_producto
            productos_modificados: Lista de productos modificados con id_producto y cambios
            productos_eliminados: Lista de productos eliminados con id_producto
            monto_anterior: Monto anterior
            monto_nuevo: Monto nuevo
            otros_cambios: Otros cambios (moneda, pago, entrega) en formato {'campo': {'anterior': X, 'nuevo': Y}}
            numero_oc: Número correlativo de la OC (ej: OC-000512-2025)
        """
        try:
            # Construir descripción
            cambios_desc = []

            if id_proveedor_anterior and id_proveedor_nuevo and id_proveedor_anterior != id_proveedor_nuevo:
                cambios_desc.append("proveedor")

            if id_contacto_anterior and id_contacto_nuevo and id_contacto_anterior != id_contacto_nuevo:
                cambios_desc.append("contacto")

            if productos_agregados:
                cambios_desc.append(f"{len(productos_agregados)} producto(s) agregado(s)")

            if productos_modificados:
                cambios_desc.append(f"{len(productos_modificados)} producto(s) modificado(s)")

            if productos_eliminados:
                cambios_desc.append(f"{len(productos_eliminados)} producto(s) eliminado(s)")

            if monto_anterior is not None and monto_nuevo is not None:
                cambios_desc.append("monto")

            if otros_cambios:
                for campo in otros_cambios.keys():
                    cambios_desc.append(campo)

            descripcion = f"Orden de compra actualizada. Cambios: {', '.join(cambios_desc) if cambios_desc else 'sin cambios detectados'}"

            # Formato concatenado para cambios
            cambio_proveedor_str = None
            if id_proveedor_anterior and id_proveedor_nuevo and id_proveedor_anterior != id_proveedor_nuevo:
                cambio_proveedor_str = f"{id_proveedor_anterior} ----> {id_proveedor_nuevo}"

            cambio_contacto_str = None
            if id_contacto_anterior and id_contacto_nuevo and id_contacto_anterior != id_contacto_nuevo:
                cambio_contacto_str = f"{id_contacto_anterior} ----> {id_contacto_nuevo}"

            cambio_monto_str = None
            if monto_anterior is not None and monto_nuevo is not None:
                cambio_monto_str = f"{monto_anterior} ----> {monto_nuevo}"

            # Productos: solo IDs
            productos_agregados_json = None
            if productos_agregados:
                ids = [str(p.get('id_producto')) for p in productos_agregados]
                productos_agregados_json = json.dumps(ids)

            productos_eliminados_json = None
            if productos_eliminados:
                ids = [str(p.get('id_producto')) for p in productos_eliminados]
                productos_eliminados_json = json.dumps(ids)

            productos_modificados_json = None
            if productos_modificados:
                # Guardar id y descripción de cambios
                mods = []
                for p in productos_modificados:
                    mods.append({
                        'id_producto': p.get('id_producto'),
                        'cambios': p.get('cambios', {})
                    })
                productos_modificados_json = json.dumps(mods)

            # Otros cambios en formato concatenado
            cambios_adicionales_json = None
            if otros_cambios:
                cambios_concatenados = {}
                for campo, valores in otros_cambios.items():
                    anterior = valores.get('anterior', '')
                    nuevo = valores.get('nuevo', '')
                    cambios_concatenados[campo] = f"{anterior} ----> {nuevo}"
                cambios_adicionales_json = json.dumps(cambios_concatenados)

            # Crear registro de auditoría
            auditoria = OrdenesCompraAuditoriaModel(
                tipo_operacion="ACTUALIZACION",
                fecha_evento=datetime.now(),
                id_orden_compra=id_orden_compra,
                numero_oc=numero_oc,  # Guardar número de OC
                id_usuario=id_usuario,
                id_cotizacion=id_cotizacion,
                id_cotizacion_versiones=id_cotizacion_versiones,
                cambio_proveedor=cambio_proveedor_str,
                cambio_contacto=cambio_contacto_str,
                cambio_monto=cambio_monto_str,
                productos_agregados=productos_agregados_json,
                productos_modificados=productos_modificados_json,
                productos_eliminados=productos_eliminados_json,
                cambios_adicionales=cambios_adicionales_json,
                descripcion=descripcion
            )

            self.db.add(auditoria)
            logger.info(f"✅ Auditoría de actualización registrada para orden {id_orden_compra}")

        except Exception as e:
            logger.error(f"❌ Error al registrar auditoría de actualización: {e}", exc_info=True)
            raise

    def registrar_eliminacion_orden(
        self,
        id_orden_compra: int,
        id_usuario: int,
        id_cotizacion: int,
        id_cotizacion_versiones: int,
        id_proveedor: int,
        id_contacto: int,
        productos: List[Dict[str, Any]],
        monto_total: float,
        numero_oc: str = None
    ) -> None:
        """
        Registra la eliminación de una orden de compra.

        Args:
            id_orden_compra: ID de la orden eliminada
            id_usuario: ID del usuario que eliminó la orden
            id_cotizacion: ID de la cotización
            id_cotizacion_versiones: ID de la versión de cotización
            id_proveedor: ID del proveedor
            id_contacto: ID del contacto
            productos: Lista de productos que tenía la orden
            monto_total: Monto total de la orden eliminada
            numero_oc: Número correlativo de la OC (ej: OC-000512-2025)
        """
        try:
            cantidad_productos = len(productos)

            # Construir descripción con número de OC si está disponible
            if numero_oc:
                descripcion = (
                    f"Orden de compra {numero_oc} (ID: {id_orden_compra}) eliminada. "
                    f"Tenía {cantidad_productos} producto(s). "
                    f"Monto total: S/ {monto_total:,.2f}"
                )
            else:
                descripcion = (
                    f"Orden de compra #{id_orden_compra} eliminada. "
                    f"Tenía {cantidad_productos} producto(s). "
                    f"Monto total: S/ {monto_total:,.2f}"
                )

            # Todos los productos pasan a eliminados
            ids_productos = [str(p.get('id_producto')) for p in productos]
            productos_eliminados_json = json.dumps(ids_productos) if ids_productos else None

            # Crear registro de auditoría
            # IMPORTANTE: id_orden_compra se deja en NULL porque la orden será eliminada
            # Esto evita el error de foreign key constraint al hacer commit
            auditoria = OrdenesCompraAuditoriaModel(
                tipo_operacion="ELIMINACION",
                fecha_evento=datetime.now(),
                id_orden_compra=None,  # NULL porque la orden será eliminada en la misma transacción
                numero_oc=numero_oc,  # Guardar número de OC para mantener historial
                id_usuario=id_usuario,
                id_cotizacion=id_cotizacion,
                id_cotizacion_versiones=id_cotizacion_versiones,
                cambio_proveedor=str(id_proveedor),
                cambio_contacto=str(id_contacto),
                cambio_monto=str(monto_total),
                productos_eliminados=productos_eliminados_json,
                descripcion=descripcion
            )

            self.db.add(auditoria)
            logger.info(f"✅ Auditoría de eliminación registrada para orden {id_orden_compra}")

        except Exception as e:
            logger.error(f"❌ Error al registrar auditoría de eliminación: {e}", exc_info=True)
            raise
