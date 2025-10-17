import logging
from datetime import datetime
from typing import List, Any

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.adapters.inbound.api.schemas.generar_oc_schemas import GenerarOCRequest
from app.adapters.outbound.database.models.marcas_model import MarcasModel
from app.adapters.outbound.database.models.ordenes_compra_detalles_model import (
    OrdenesCompraDetallesModel,
)
from app.adapters.outbound.database.models.ordenes_compra_model import (
    OrdenesCompraModel,
)
from app.adapters.outbound.database.models.productos_model import ProductosModel
from app.adapters.outbound.database.models.proveedor_contacto_model import (
    ProveedorContactosModel,
)
from app.adapters.outbound.database.models.proveedor_detalle_model import (
    ProveedorDetalleModel,
)
from app.adapters.outbound.database.models.proveedores_model import ProveedoresModel
from app.adapters.outbound.database.models.unidad_medida_model import UnidadMedidaModel
from app.core.domain.entities.ordenes_compra import OrdenesCompra
from app.core.infrastructure.events.event_dispatcher import get_event_dispatcher
from app.core.ports.repositories.ordenes_compra_repository import (
    OrdenesCompraRepositoryPort,
)

logger = logging.getLogger(__name__)


def _handle_orden_compra_evento(event_data: dict):
    """
    Handler que se ejecuta en thread separado con NUEVA transacción
    Equivalente a @Transactional(propagation = REQUIRES_NEW)

    Este método se ejecuta DESPUÉS del commit exitoso de la OC

    Args:
        event_data: Datos del evento
    """
    from app.dependencies import get_db
    from app.core.use_cases.registro_compra.procesar_registro_compra import ProcesarRegistroCompra

    # NUEVA SESIÓN DB (transacción independiente)
    db = next(get_db())

    try:
        logger.info(f"🔄 Procesando evento en thread separado: {event_data.get('tipo_evento')}")

        # Ejecutar caso de uso de procesamiento
        use_case = ProcesarRegistroCompra(db)
        use_case.execute(event_data)

        logger.info(f"✅ Evento procesado exitosamente")

    except Exception as e:
        logger.error(f"❌ Error en handler de evento: {e}", exc_info=True)
        # No propagar error - ya está en thread separado

    finally:
        db.close()


class OrdenesCompraRepository(OrdenesCompraRepositoryPort):

    def __init__(self, db: Session):
        self.db = db
        self.event_dispatcher = get_event_dispatcher()

    def save(self, order: OrdenesCompra) -> OrdenesCompra:
        """
        DEPRECADO: Usar save_batch() en su lugar.
        Este método guarda una sola orden y dispara un evento por cada orden.
        Para evitar múltiples eventos, usar save_batch() que procesa todas las órdenes en una transacción.
        """
        logger.warning("⚠️ Método save() está deprecado. Usar save_batch() en su lugar.")
        return self.save_batch([order])[0]

    def save_batch(self, orders: List[OrdenesCompra]) -> List[OrdenesCompra]:
        """
        Guarda múltiples órdenes de compra en una sola transacción
        y dispara el evento UNA SOLA VEZ al final
        
        Args:
            orders: Lista de órdenes de compra a guardar
            
        Returns:
            Lista de órdenes guardadas
        """
        try:
            if not orders:
                return []
            
            # Obtener el último correlativo
            last_correlative = (
                self.db.query(OrdenesCompraModel)
                .order_by(OrdenesCompraModel.id_orden.desc())
                .first()
            )
            if last_correlative:
                last_number = int(last_correlative.correlative.split("-")[1])
            else:
                last_number = 0

            current_year = datetime.now().year
            saved_orders = []
            
            # Guardar todas las órdenes sin commit
            for idx, order in enumerate(orders):
                new_number = last_number + idx + 1
                new_correlative = f"OC-{new_number:06d}-{current_year}"
                print(f"Este es el correlativo: {new_correlative}")

                # Calcular total de la orden
                total_orden = sum(item.p_total for item in order.items)

                db_order = OrdenesCompraModel(
                    id_cotizacion=order.id_cotizacion,
                    id_proveedor=order.id_proveedor,
                    id_proveedor_contacto=order.id_proveedor_contacto,
                    moneda=order.moneda,
                    pago=order.pago,
                    entrega=order.entrega,
                    id_cotizacion_versiones=order.id_cotizacion_versiones,
                    fecha_creacion=datetime.now(),
                    correlative=new_correlative,
                    id_usuario=order.id_usuario,
                    consorcio=order.consorcio,
                    total=str(total_orden)
                )

                self.db.add(db_order)
                self.db.flush()  # Obtener ID sin commit

                # Insertar detalles
                for item in order.items:
                    db_detail = OrdenesCompraDetallesModel(
                        id_orden=db_order.id_orden,
                        id_producto=item.id_producto,
                        cantidad=item.cantidad,
                        precio_unitario=item.p_unitario,
                        precio_total=item.p_total,
                    )
                    self.db.add(db_detail)
                
                saved_orders.append(order)
                print(f"Orden {db_order.id_orden} preparada para guardado en batch")

            # Publicar UN SOLO EVENTO para todas las órdenes
            # Usamos los datos de la primera orden para el evento (todas son de la misma cotización/versión)
            first_order = orders[0]
            self.event_dispatcher.publish(
                session=self.db,
                event_data={
                    'tipo_evento': 'ORDEN_COMPRA_CREADA',
                    'id_cotizacion': first_order.id_cotizacion,
                    'id_cotizacion_versiones': first_order.id_cotizacion_versiones,
                    'cantidad_ordenes': len(orders),
                    'consorcio': first_order.consorcio if first_order.consorcio else False
                },
                handler=_handle_orden_compra_evento
            )

            # Commit de todas las órdenes de una sola vez
            self.db.commit()

            logger.info(f"✅ {len(orders)} órdenes guardadas en batch - Evento será procesado en background")

            return saved_orders

        except Exception as e:
            self.db.rollback()
            print(f"Error al guardar órdenes en batch: {e}")
            raise e

    def obtener_info_oc(self, request: GenerarOCRequest) -> List[Any]:
        """
        Obtiene información de productos para generar orden de compra desde las tablas de órdenes ya guardadas

        Args:
            request (GenerarOCRequest): Datos de la solicitud

        Returns:
            List[Any]: Lista de resultados de la consulta
        """
        try:
            print(
                f"Ejecutando consulta para cotización: {request.id_cotizacion}, versión: {request.id_version}"
            )
            print(f"Contactos de proveedor: {request.id_contacto_proveedor}")

            latest_order_id_subquery = (
                self.db.query(OrdenesCompraModel.id_orden)
                .filter(
                    OrdenesCompraModel.id_cotizacion == request.id_cotizacion,
                    OrdenesCompraModel.id_cotizacion_versiones == request.id_version,
                    OrdenesCompraModel.id_proveedor_contacto.in_(
                        request.id_contacto_proveedor
                    ),
                )
                .order_by(
                    OrdenesCompraModel.id_orden.desc()  # Ordenamos por ID descendente para obtener el último
                )
                .limit(1)
                .scalar_subquery()
            )

            query = (
                self.db.query(
                    OrdenesCompraModel.correlative.label("NUMERO_OC"),
                    OrdenesCompraModel.id_cotizacion.label("IDCOTIZACION"),
                    OrdenesCompraModel.id_cotizacion_versiones.label("IDVERSION"),
                    OrdenesCompraDetallesModel.cantidad.label("CANT"),
                    UnidadMedidaModel.descripcion.label("UMED"),
                    ProductosModel.nombre.label("PRODUCTO"),
                    MarcasModel.nombre.label("MARCA"),
                    ProductosModel.modelo_marca.label("MODELO"),
                    func.date(OrdenesCompraModel.fecha_creacion).label("FECHA"),
                    ProveedoresModel.id_proveedor.label("IDPROVEEDOR"),
                    ProveedoresModel.razon_social.label("PROVEEDOR"),
                    OrdenesCompraModel.id_proveedor_contacto.label(
                        "IDPROVEEDORCONTACTO"
                    ),
                    ProveedorContactosModel.nombre.label("PERSONAL"),
                    ProveedorContactosModel.telefono.label("TELEFONO"),
                    ProveedorContactosModel.celular.label("CELULAR"),
                    ProveedorContactosModel.correo.label("CORREO"),
                    ProveedoresModel.direccion.label("DIRECCION"),
                    OrdenesCompraModel.moneda.label("MONEDA"),
                    OrdenesCompraModel.pago.label("PAGO"),
                    OrdenesCompraDetallesModel.precio_unitario.label("PUNIT"),
                    case(
                        (ProveedorDetalleModel.igv == "SIN IGV", "SIN IGV"),
                        else_=ProveedorDetalleModel.igv == "CON IGV",
                    ).label("IGV"),
                    OrdenesCompraDetallesModel.precio_total.label("TOTAL"),
                )
                .select_from(OrdenesCompraModel)
                .join(
                    OrdenesCompraDetallesModel,
                    OrdenesCompraModel.id_orden == OrdenesCompraDetallesModel.id_orden,
                )
                .join(
                    ProductosModel,
                    OrdenesCompraDetallesModel.id_producto
                    == ProductosModel.id_producto,
                )
                .join(
                    UnidadMedidaModel,
                    ProductosModel.id_unidad_medida
                    == UnidadMedidaModel.id_unidad_medida,
                )
                .join(MarcasModel, ProductosModel.id_marca == MarcasModel.id_marca)
                .join(
                    ProveedoresModel,
                    OrdenesCompraModel.id_proveedor == ProveedoresModel.id_proveedor,
                )
                .join(
                    ProveedorDetalleModel,
                    ProductosModel.id_producto == ProveedorDetalleModel.id_producto,
                )
                .join(
                    ProveedorContactosModel,
                    OrdenesCompraModel.id_proveedor_contacto
                    == ProveedorContactosModel.id_proveedor_contacto,
                )
                .filter(OrdenesCompraModel.id_orden == latest_order_id_subquery)
            )

            resultados = query.all()
            print(f"Consulta ejecutada. Resultados obtenidos: {len(resultados)}")

            if resultados:
                print(f"Primer resultado: {resultados[0]}")

            return resultados

        except Exception as e:
            print(f"Error en obtener_info_oc: {e}")
            import traceback

            traceback.print_exc()
            return []

    def actualizar_ruta_s3(self, id_orden: int, ruta_s3: str) -> bool:
        """
        Actualiza la ruta S3 de una orden de compra específica

        Args:
            id_orden (int): ID de la orden de compra
            ruta_s3 (str): URL del archivo en S3

        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        try:
            orden = (
                self.db.query(OrdenesCompraModel)
                .filter(OrdenesCompraModel.id_orden == id_orden)
                .first()
            )
            print(f"Este es el orden: {orden}")

            if orden:
                orden.ruta_s3 = ruta_s3
                self.db.commit()
                print(f"URL S3 actualizada para orden {id_orden}: {ruta_s3}")
                return True
            else:
                print(f"No se encontró orden con ID {id_orden}")
                return False

        except Exception as e:
            print(f"Error al actualizar ruta S3: {e}")
            self.db.rollback()
            return False

    def obtener_ordenes_por_contacto_y_version(
        self, id_cotizacion: int, id_version: int, id_contacto: int
    ) -> list[type[OrdenesCompraModel]] | list[Any]:
        """
        Obtiene las órdenes de compra de un contacto específico en una versión de cotización

        Args:
            id_cotizacion (int): ID de la cotización
            id_version (int): ID de la versión
            id_contacto (int): ID del contacto del proveedor

        Returns:
            List[OrdenesCompraModel]: Lista de órdenes encontradas

        """

        try:
            query = self.db.query(OrdenesCompraModel).filter(
                OrdenesCompraModel.id_cotizacion == id_cotizacion,
                OrdenesCompraModel.id_cotizacion_versiones == id_version,
                OrdenesCompraModel.id_proveedor_contacto == id_contacto,
            )

            query = query.order_by(OrdenesCompraModel.id_orden.desc())
            latest_order = query.first()

            if latest_order:
                return [latest_order]
            else:
                return []

        except Exception as e:
            print(f"Error al obtener órdenes por contacto: {e}")
            return []

    def obtener_orden_por_id(self, id_orden: int) -> OrdenesCompra:
        """
        Obtiene una orden de compra por su ID

        Args:
            id_orden (int): ID de la orden de compra

        Returns:
            OrdenesCompra: Orden de compra encontrada

        Raises:
            ValueError: Si la orden no existe
        """
        try:
            orden = (
                self.db.query(OrdenesCompraModel)
                .filter(OrdenesCompraModel.id_orden == id_orden)
                .first()
            )

            if not orden:
                raise ValueError(f"Orden de compra con ID {id_orden} no encontrada")

            return orden

        except Exception as e:
            logger.error(f"Error al obtener orden por ID {id_orden}: {e}")
            raise

    def eliminar_orden(self, id_orden: int) -> bool:
        """
        Elimina una orden de compra y todos sus registros asociados

        Args:
            id_orden (int): ID de la orden de compra

        Returns:
            bool: True si se eliminó correctamente, False en caso contrario

        Raises:
            ValueError: Si la orden no existe
        """
        from app.adapters.outbound.database.models.registro_compra_orden_model import RegistroCompraOrdenModel

        try:
            # Verificar que la orden existe
            orden = (
                self.db.query(OrdenesCompraModel)
                .filter(OrdenesCompraModel.id_orden == id_orden)
                .first()
            )

            if not orden:
                raise ValueError(f"Orden de compra con ID {id_orden} no encontrada")

            # 1. Eliminar registro_compra_ordenes primero (FK a ordenes_compra)
            deleted_registros = self.db.query(RegistroCompraOrdenModel).filter(
                RegistroCompraOrdenModel.id_orden == id_orden
            ).delete()

            if deleted_registros > 0:
                logger.info(f"Eliminados {deleted_registros} registros de compra asociados")

            # 2. Eliminar detalles de la orden (FK a ordenes_compra)
            deleted_detalles = self.db.query(OrdenesCompraDetallesModel).filter(
                OrdenesCompraDetallesModel.id_orden == id_orden
            ).delete()

            logger.info(f"Eliminados {deleted_detalles} detalles de la orden")

            # 3. Eliminar la orden
            self.db.query(OrdenesCompraModel).filter(
                OrdenesCompraModel.id_orden == id_orden
            ).delete()

            self.db.commit()
            logger.info(f"Orden de compra {id_orden} eliminada exitosamente")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al eliminar orden de compra {id_orden}: {e}")
            raise

    def actualizar_orden(self, id_orden: int, moneda: str = None, pago: str = None, entrega: str = None) -> bool:
        """
        Actualiza los campos básicos de una orden de compra

        Args:
            id_orden (int): ID de la orden de compra
            moneda (str, optional): Nueva moneda
            pago (str, optional): Nueva forma de pago
            entrega (str, optional): Nuevas condiciones de entrega

        Returns:
            bool: True si se actualizó correctamente

        Raises:
            ValueError: Si la orden no existe
        """
        try:
            orden = (
                self.db.query(OrdenesCompraModel)
                .filter(OrdenesCompraModel.id_orden == id_orden)
                .first()
            )

            if not orden:
                raise ValueError(f"Orden de compra con ID {id_orden} no encontrada")

            # Actualizar solo los campos que se proporcionaron
            if moneda is not None:
                orden.moneda = moneda
            if pago is not None:
                orden.pago = pago
            if entrega is not None:
                orden.entrega = entrega

            self.db.commit()
            logger.info(f"Orden de compra {id_orden} actualizada exitosamente")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al actualizar orden de compra {id_orden}: {e}")
            raise

    def obtener_detalles_orden(self, id_orden: int) -> List[Any]:
        """
        Obtiene los detalles de una orden de compra

        Args:
            id_orden (int): ID de la orden de compra

        Returns:
            List[Any]: Lista de detalles de la orden
        """
        try:
            detalles = (
                self.db.query(OrdenesCompraDetallesModel)
                .filter(OrdenesCompraDetallesModel.id_orden == id_orden)
                .all()
            )
            return detalles

        except Exception as e:
            logger.error(f"Error al obtener detalles de orden {id_orden}: {e}")
            raise

    def actualizar_detalle_producto(self, id_oc_detalle: int, cantidad: int, precio_unitario: float, precio_total: float) -> bool:
        """
        Actualiza un detalle de producto existente

        Args:
            id_oc_detalle (int): ID del detalle de la orden
            cantidad (int): Nueva cantidad
            precio_unitario (float): Nuevo precio unitario
            precio_total (float): Nuevo precio total

        Returns:
            bool: True si se actualizó correctamente

        Raises:
            ValueError: Si el detalle no existe
        """
        try:
            detalle = (
                self.db.query(OrdenesCompraDetallesModel)
                .filter(OrdenesCompraDetallesModel.id_oc_detalle == id_oc_detalle)
                .first()
            )

            if not detalle:
                raise ValueError(f"Detalle de orden con ID {id_oc_detalle} no encontrado")

            detalle.cantidad = cantidad
            detalle.precio_unitario = precio_unitario
            detalle.precio_total = precio_total

            self.db.commit()
            logger.info(f"Detalle {id_oc_detalle} actualizado exitosamente")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al actualizar detalle {id_oc_detalle}: {e}")
            raise

    def crear_detalle_producto(self, id_orden: int, id_producto: int, cantidad: int, precio_unitario: float, precio_total: float) -> Any:
        """
        Crea un nuevo detalle de producto

        Args:
            id_orden (int): ID de la orden de compra
            id_producto (int): ID del producto
            cantidad (int): Cantidad
            precio_unitario (float): Precio unitario
            precio_total (float): Precio total

        Returns:
            Any: Detalle creado
        """
        try:
            nuevo_detalle = OrdenesCompraDetallesModel(
                id_orden=id_orden,
                id_producto=id_producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                precio_total=precio_total
            )

            self.db.add(nuevo_detalle)
            self.db.commit()
            self.db.refresh(nuevo_detalle)

            logger.info(f"Nuevo detalle creado para orden {id_orden}, producto {id_producto}")
            return nuevo_detalle

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al crear detalle: {e}")
            raise

    def eliminar_detalle_producto(self, id_oc_detalle: int) -> bool:
        """
        Elimina un detalle de producto

        Args:
            id_oc_detalle (int): ID del detalle de la orden

        Returns:
            bool: True si se eliminó correctamente

        Raises:
            ValueError: Si el detalle no existe
        """
        try:
            detalle = (
                self.db.query(OrdenesCompraDetallesModel)
                .filter(OrdenesCompraDetallesModel.id_oc_detalle == id_oc_detalle)
                .first()
            )

            if not detalle:
                raise ValueError(f"Detalle de orden con ID {id_oc_detalle} no encontrado")

            self.db.delete(detalle)
            self.db.commit()

            logger.info(f"Detalle {id_oc_detalle} eliminado exitosamente")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al eliminar detalle {id_oc_detalle}: {e}")
            raise

    def obtener_orden_completa(self, id_orden: int) -> Any:
        """
        Obtiene la orden completa con todos sus datos (proveedor, contacto, productos)

        Args:
            id_orden (int): ID de la orden de compra

        Returns:
            Any: Diccionario con toda la información de la orden

        Raises:
            ValueError: Si la orden no existe
        """
        try:
            # Consulta principal similar a obtener_info_oc pero filtrada por id_orden
            query = (
                self.db.query(
                    OrdenesCompraModel.id_orden.label("ID_ORDEN"),
                    OrdenesCompraModel.correlative.label("NUMERO_OC"),
                    OrdenesCompraModel.id_cotizacion.label("IDCOTIZACION"),
                    OrdenesCompraModel.id_cotizacion_versiones.label("IDVERSION"),
                    func.date(OrdenesCompraModel.fecha_creacion).label("FECHA"),
                    OrdenesCompraModel.moneda.label("MONEDA"),
                    OrdenesCompraModel.pago.label("PAGO"),
                    OrdenesCompraModel.entrega.label("ENTREGA"),
                    OrdenesCompraModel.total.label("TOTAL_ORDEN"),
                    OrdenesCompraModel.ruta_s3.label("RUTA_S3"),
                    # Datos del proveedor
                    ProveedoresModel.id_proveedor.label("IDPROVEEDOR"),
                    ProveedoresModel.razon_social.label("PROVEEDOR"),
                    ProveedoresModel.direccion.label("DIRECCION"),
                    # Datos del contacto
                    OrdenesCompraModel.id_proveedor_contacto.label("IDPROVEEDORCONTACTO"),
                    ProveedorContactosModel.nombre.label("PERSONAL"),
                    ProveedorContactosModel.telefono.label("TELEFONO"),
                    ProveedorContactosModel.celular.label("CELULAR"),
                    ProveedorContactosModel.correo.label("CORREO"),
                    # Datos del detalle/producto
                    OrdenesCompraDetallesModel.id_oc_detalle.label("ID_OC_DETALLE"),
                    OrdenesCompraDetallesModel.id_producto.label("IDPRODUCTO"),
                    ProductosModel.nombre.label("PRODUCTO"),
                    MarcasModel.nombre.label("MARCA"),
                    ProductosModel.modelo_marca.label("MODELO"),
                    UnidadMedidaModel.descripcion.label("UMED"),
                    OrdenesCompraDetallesModel.cantidad.label("CANT"),
                    OrdenesCompraDetallesModel.precio_unitario.label("PUNIT"),
                    OrdenesCompraDetallesModel.precio_total.label("TOTAL"),
                    case(
                        (ProveedorDetalleModel.igv == "SIN IGV", "SIN IGV"),
                        else_="CON IGV",
                    ).label("IGV"),
                )
                .select_from(OrdenesCompraModel)
                .join(
                    OrdenesCompraDetallesModel,
                    OrdenesCompraModel.id_orden == OrdenesCompraDetallesModel.id_orden,
                )
                .join(
                    ProductosModel,
                    OrdenesCompraDetallesModel.id_producto == ProductosModel.id_producto,
                )
                .join(
                    UnidadMedidaModel,
                    ProductosModel.id_unidad_medida == UnidadMedidaModel.id_unidad_medida,
                )
                .join(MarcasModel, ProductosModel.id_marca == MarcasModel.id_marca)
                .join(
                    ProveedoresModel,
                    OrdenesCompraModel.id_proveedor == ProveedoresModel.id_proveedor,
                )
                .join(
                    ProveedorDetalleModel,
                    ProductosModel.id_producto == ProveedorDetalleModel.id_producto,
                )
                .join(
                    ProveedorContactosModel,
                    OrdenesCompraModel.id_proveedor_contacto
                    == ProveedorContactosModel.id_proveedor_contacto,
                )
                .filter(OrdenesCompraModel.id_orden == id_orden)
            )

            resultados = query.all()

            if not resultados:
                raise ValueError(f"Orden de compra con ID {id_orden} no encontrada")

            logger.info(f"Orden completa {id_orden} obtenida con {len(resultados)} productos")
            return resultados

        except Exception as e:
            logger.error(f"Error al obtener orden completa {id_orden}: {e}")
            raise
