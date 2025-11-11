"""
Servicio de auditoría para órdenes de compra.

Este servicio registra todos los cambios (creación, actualización, eliminación)
en las órdenes de compra para mantener un historial completo de auditoría,
incluyendo cambios en proveedor, contacto y productos.
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
    Servicio para registrar cambios detallados en órdenes de compra.

    Este servicio registra:
    - Creación de órdenes
    - Actualización de órdenes (con cambios de proveedor, contacto y productos)
    - Eliminación de órdenes
    """

    def __init__(self, db: Session):
        self.db = db

    def registrar_creacion_orden(
        self,
        id_orden_compra: int,
        numero_oc: str,
        id_usuario: int,
        id_cotizacion: int,
        id_cotizacion_versiones: int,
        id_proveedor: int,
        nombre_proveedor: str,
        id_contacto: int,
        nombre_contacto: str,
        productos: List[Dict[str, Any]],
        monto_total: float,
        otros_datos: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Registra la creación de una nueva orden de compra.

        Args:
            id_orden_compra: ID de la orden creada
            numero_oc: Número correlativo de la OC
            id_usuario: ID del usuario que creó la orden
            id_cotizacion: ID de la cotización
            id_cotizacion_versiones: ID de la versión de cotización
            id_proveedor: ID del proveedor
            nombre_proveedor: Razón social del proveedor
            id_contacto: ID del contacto
            nombre_contacto: Nombre del contacto
            productos: Lista de productos agregados
            monto_total: Monto total de la orden
            otros_datos: Otros datos opcionales (moneda, pago, entrega, etc.)
        """
        try:
            cantidad_productos = len(productos)

            descripcion = (
                f"Orden de compra {numero_oc} creada. "
                f"Proveedor: {nombre_proveedor}. "
                f"Contacto: {nombre_contacto}. "
                f"Productos: {cantidad_productos}. "
                f"Total: S/ {monto_total:,.2f}"
            )

            # Preparar JSON de productos agregados
            productos_json = json.dumps([{
                'id_producto': p.get('id_producto'),
                'nombre': p.get('nombre', 'N/A'),
                'cantidad': p.get('cantidad'),
                'precio_unitario': float(p.get('precio_unitario', 0)),
                'precio_total': float(p.get('precio_total', 0))
            } for p in productos], default=str)

            auditoria = OrdenesCompraAuditoriaModel(
                fecha_evento=datetime.now(),
                tipo_operacion="CREACION",
                id_orden_compra=id_orden_compra,
                numero_oc=numero_oc,
                id_usuario=id_usuario,
                id_cotizacion=id_cotizacion,
                id_cotizacion_versiones=id_cotizacion_versiones,
                # Datos del proveedor (solo nuevo en creación)
                id_proveedor_nuevo=id_proveedor,
                proveedor_nuevo=nombre_proveedor,
                # Datos del contacto (solo nuevo en creación)
                id_contacto_nuevo=id_contacto,
                contacto_nuevo=nombre_contacto,
                # Productos agregados
                productos_agregados=productos_json,
                # Monto
                monto_nuevo=monto_total,
                # Descripción
                descripcion=descripcion,
                # Metadata adicional
                cambios_adicionales=json.dumps(otros_datos, default=str) if otros_datos else None
            )

            self.db.add(auditoria)
            logger.info(f"Auditoría registrada (pendiente commit): Creación de OC {numero_oc}")

        except Exception as e:
            logger.error(f"Error al registrar auditoría de creación de OC: {e}", exc_info=True)
            raise

    def registrar_actualizacion_orden(
        self,
        id_orden_compra: int,
        numero_oc: str,
        id_usuario: int,
        id_cotizacion: int,
        id_cotizacion_versiones: int,
        # Datos de proveedor (opcional si cambió)
        id_proveedor_anterior: Optional[int] = None,
        nombre_proveedor_anterior: Optional[str] = None,
        id_proveedor_nuevo: Optional[int] = None,
        nombre_proveedor_nuevo: Optional[str] = None,
        # Datos de contacto (opcional si cambió)
        id_contacto_anterior: Optional[int] = None,
        nombre_contacto_anterior: Optional[str] = None,
        id_contacto_nuevo: Optional[int] = None,
        nombre_contacto_nuevo: Optional[str] = None,
        # Cambios en productos
        productos_agregados: Optional[List[Dict[str, Any]]] = None,
        productos_modificados: Optional[List[Dict[str, Any]]] = None,
        productos_eliminados: Optional[List[Dict[str, Any]]] = None,
        # Montos
        monto_anterior: Optional[float] = None,
        monto_nuevo: Optional[float] = None,
        # Otros cambios
        otros_cambios: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Registra la actualización de una orden de compra.

        Args:
            id_orden_compra: ID de la orden actualizada
            numero_oc: Número correlativo de la OC
            id_usuario: ID del usuario que actualizó
            id_cotizacion: ID de la cotización
            id_cotizacion_versiones: ID de la versión de cotización
            id_proveedor_anterior: ID del proveedor anterior (si cambió)
            nombre_proveedor_anterior: Nombre del proveedor anterior (si cambió)
            id_proveedor_nuevo: ID del proveedor nuevo (si cambió)
            nombre_proveedor_nuevo: Nombre del proveedor nuevo (si cambió)
            id_contacto_anterior: ID del contacto anterior (si cambió)
            nombre_contacto_anterior: Nombre del contacto anterior (si cambió)
            id_contacto_nuevo: ID del contacto nuevo (si cambió)
            nombre_contacto_nuevo: Nombre del contacto nuevo (si cambió)
            productos_agregados: Lista de productos agregados
            productos_modificados: Lista de productos modificados
            productos_eliminados: Lista de productos eliminados
            monto_anterior: Monto anterior
            monto_nuevo: Monto nuevo
            otros_cambios: Otros cambios (moneda, pago, entrega)
        """
        try:
            # Construir descripción dinámica
            cambios_descripcion = []

            # Cambio de proveedor
            if id_proveedor_anterior and id_proveedor_nuevo and id_proveedor_anterior != id_proveedor_nuevo:
                cambios_descripcion.append(
                    f"Proveedor: {nombre_proveedor_anterior} → {nombre_proveedor_nuevo}"
                )

            # Cambio de contacto
            if id_contacto_anterior and id_contacto_nuevo and id_contacto_anterior != id_contacto_nuevo:
                cambios_descripcion.append(
                    f"Contacto: {nombre_contacto_anterior} → {nombre_contacto_nuevo}"
                )

            # Cambios en productos
            if productos_agregados and len(productos_agregados) > 0:
                cambios_descripcion.append(f"{len(productos_agregados)} producto(s) agregado(s)")

            if productos_modificados and len(productos_modificados) > 0:
                cambios_descripcion.append(f"{len(productos_modificados)} producto(s) modificado(s)")

            if productos_eliminados and len(productos_eliminados) > 0:
                cambios_descripcion.append(f"{len(productos_eliminados)} producto(s) eliminado(s)")

            # Cambio de monto
            if monto_anterior is not None and monto_nuevo is not None and monto_anterior != monto_nuevo:
                diferencia = monto_nuevo - monto_anterior
                signo = "+" if diferencia > 0 else ""
                cambios_descripcion.append(
                    f"Total: S/ {monto_anterior:,.2f} → S/ {monto_nuevo:,.2f} ({signo}S/ {diferencia:,.2f})"
                )

            # Otros cambios
            if otros_cambios:
                for campo, valores in otros_cambios.items():
                    if isinstance(valores, dict) and 'anterior' in valores and 'nuevo' in valores:
                        if valores['anterior'] != valores['nuevo']:
                            cambios_descripcion.append(
                                f"{campo.capitalize()}: {valores['anterior']} → {valores['nuevo']}"
                            )

            descripcion = (
                f"Orden de compra {numero_oc} actualizada. "
                f"Cambios: {'. '.join(cambios_descripcion) if cambios_descripcion else 'Sin cambios significativos'}"
            )

            # Preparar JSON de productos
            productos_agregados_json = None
            if productos_agregados:
                productos_agregados_json = json.dumps([{
                    'id_producto': p.get('id_producto'),
                    'nombre': p.get('nombre', 'N/A'),
                    'cantidad': p.get('cantidad'),
                    'precio_unitario': float(p.get('precio_unitario', 0)),
                    'precio_total': float(p.get('precio_total', 0))
                } for p in productos_agregados], default=str)

            productos_modificados_json = None
            if productos_modificados:
                productos_modificados_json = json.dumps([{
                    'id_producto': p.get('id_producto'),
                    'nombre': p.get('nombre', 'N/A'),
                    'cantidad_anterior': p.get('cantidad_anterior'),
                    'cantidad_nueva': p.get('cantidad_nueva'),
                    'precio_anterior': float(p.get('precio_anterior', 0)),
                    'precio_nuevo': float(p.get('precio_nuevo', 0))
                } for p in productos_modificados], default=str)

            productos_eliminados_json = None
            if productos_eliminados:
                productos_eliminados_json = json.dumps([{
                    'id_producto': p.get('id_producto'),
                    'nombre': p.get('nombre', 'N/A'),
                    'cantidad': p.get('cantidad'),
                    'precio_total': float(p.get('precio_total', 0))
                } for p in productos_eliminados], default=str)

            auditoria = OrdenesCompraAuditoriaModel(
                fecha_evento=datetime.now(),
                tipo_operacion="ACTUALIZACION",
                id_orden_compra=id_orden_compra,
                numero_oc=numero_oc,
                id_usuario=id_usuario,
                id_cotizacion=id_cotizacion,
                id_cotizacion_versiones=id_cotizacion_versiones,
                # Cambios de proveedor
                id_proveedor_anterior=id_proveedor_anterior,
                proveedor_anterior=nombre_proveedor_anterior,
                id_proveedor_nuevo=id_proveedor_nuevo,
                proveedor_nuevo=nombre_proveedor_nuevo,
                # Cambios de contacto
                id_contacto_anterior=id_contacto_anterior,
                contacto_anterior=nombre_contacto_anterior,
                id_contacto_nuevo=id_contacto_nuevo,
                contacto_nuevo=nombre_contacto_nuevo,
                # Productos
                productos_agregados=productos_agregados_json,
                productos_modificados=productos_modificados_json,
                productos_eliminados=productos_eliminados_json,
                # Montos
                monto_anterior=monto_anterior,
                monto_nuevo=monto_nuevo,
                # Descripción
                descripcion=descripcion,
                # Otros cambios
                cambios_adicionales=json.dumps(otros_cambios, default=str) if otros_cambios else None
            )

            self.db.add(auditoria)
            logger.info(f"Auditoría registrada (pendiente commit): Actualización de OC {numero_oc}")

        except Exception as e:
            logger.error(f"Error al registrar auditoría de actualización de OC: {e}", exc_info=True)
            raise

    def registrar_eliminacion_orden(
        self,
        id_orden_compra: int,
        numero_oc: str,
        id_usuario: int,
        id_cotizacion: int,
        id_cotizacion_versiones: int,
        id_proveedor: int,
        nombre_proveedor: str,
        id_contacto: int,
        nombre_contacto: str,
        productos: List[Dict[str, Any]],
        monto_total: float,
        razon: Optional[str] = None
    ) -> None:
        """
        Registra la eliminación de una orden de compra.

        Args:
            id_orden_compra: ID de la orden eliminada
            numero_oc: Número correlativo de la OC
            id_usuario: ID del usuario que eliminó
            id_cotizacion: ID de la cotización
            id_cotizacion_versiones: ID de la versión de cotización
            id_proveedor: ID del proveedor
            nombre_proveedor: Razón social del proveedor
            id_contacto: ID del contacto
            nombre_contacto: Nombre del contacto
            productos: Lista de productos que tenía la orden
            monto_total: Monto total de la orden
            razon: Razón de la eliminación (opcional)
        """
        try:
            cantidad_productos = len(productos)

            descripcion = (
                f"Orden de compra {numero_oc} eliminada. "
                f"Proveedor: {nombre_proveedor}. "
                f"Contacto: {nombre_contacto}. "
                f"Productos eliminados: {cantidad_productos}. "
                f"Total: S/ {monto_total:,.2f}"
            )

            if razon:
                descripcion += f". Razón: {razon}"

            # Preparar JSON de productos eliminados
            productos_json = json.dumps([{
                'id_producto': p.get('id_producto'),
                'nombre': p.get('nombre', 'N/A'),
                'cantidad': p.get('cantidad'),
                'precio_unitario': float(p.get('precio_unitario', 0)),
                'precio_total': float(p.get('precio_total', 0))
            } for p in productos], default=str)

            auditoria = OrdenesCompraAuditoriaModel(
                fecha_evento=datetime.now(),
                tipo_operacion="ELIMINACION",
                id_orden_compra=id_orden_compra,
                numero_oc=numero_oc,
                id_usuario=id_usuario,
                id_cotizacion=id_cotizacion,
                id_cotizacion_versiones=id_cotizacion_versiones,
                # Datos del proveedor (solo anterior en eliminación)
                id_proveedor_anterior=id_proveedor,
                proveedor_anterior=nombre_proveedor,
                # Datos del contacto (solo anterior en eliminación)
                id_contacto_anterior=id_contacto,
                contacto_anterior=nombre_contacto,
                # Productos eliminados
                productos_eliminados=productos_json,
                # Monto
                monto_anterior=monto_total,
                # Descripción
                descripcion=descripcion,
                razon=razon
            )

            self.db.add(auditoria)
            logger.info(f"Auditoría registrada (pendiente commit): Eliminación de OC {numero_oc}")

        except Exception as e:
            logger.error(f"Error al registrar auditoría de eliminación de OC: {e}", exc_info=True)
            raise
