from fastapi import APIRouter
from app.adapters.inbound.api.schemas.ordenes_compra_schemas import (
    OrdenesCompraRequest,
    ActualizarOrdenCompraRequest,
    OrdenCompraDetalleResponse
)
from app.core.use_cases.generar_oc.generar_orden_compra import GenerarOrdenCompra
from app.core.use_cases.generar_oc.eliminar_orden_compra import EliminarOrdenCompra
from app.core.use_cases.generar_oc.actualizar_orden_compra import ActualizarOrdenCompra
from app.core.use_cases.generar_oc.obtener_orden_compra import ObtenerOrdenCompra
from fastapi import Depends
from app.dependencies import (
    get_generate_purchase_order_use_case,
    get_delete_purchase_order_use_case,
    get_update_purchase_order_use_case,
    get_obtener_purchase_order_use_case
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ordenes-compra", tags=["Ordenes de Compra"])

@router.post("/generar")
async def create_order(order: OrdenesCompraRequest, use_case: GenerarOrdenCompra = Depends(get_generate_purchase_order_use_case)):
    try:
        logger.info("=" * 80)
        logger.info("🚀 INICIO - Creación de órdenes de compra")
        logger.info(f"📦 Request: {len(order.data)} órdenes a procesar")
        print("=" * 80)
        print("🚀 INICIO - Creación de órdenes de compra")
        print(f"📦 Request: {len(order.data)} órdenes a procesar")

        urls = await use_case.execute(order)

        logger.info(f"✅ FIN - {len(urls)} URLs generadas")
        logger.info("=" * 80)
        print(f"✅ FIN - {len(urls)} URLs generadas")
        print("=" * 80)
        return {"status": "Órdenes de compra generadas", "urls": urls}
    except Exception as e:
        logger.error(f"❌ ERROR en create_order: {e}")
        logger.error(f"Tipo de error: {type(e)}")
        import traceback
        logger.error(traceback.format_exc())
        print(f"❌ ERROR en create_order: {e}")
        raise


@router.get("/{id_orden}", response_model=OrdenCompraDetalleResponse)
def get_order(
    id_orden: int,
    use_case: ObtenerOrdenCompra = Depends(get_obtener_purchase_order_use_case)
):
    """
    Obtiene una orden de compra completa por su ID.

    Este endpoint retorna:
    - Datos generales de la orden (número OC, fecha, moneda, pago, entrega, total)
    - Datos del proveedor (razón social, dirección)
    - Datos del contacto (nombre, teléfono, celular, correo)
    - Lista completa de productos con sus detalles

    Args:
        id_orden (int): ID de la orden de compra

    Returns:
        OrdenCompraDetalleResponse: Datos completos de la orden
    """
    try:
        logger.info("=" * 80)
        logger.info(f"📋 INICIO - Obtención de orden de compra ID: {id_orden}")
        print("=" * 80)
        print(f"📋 INICIO - Obtención de orden de compra ID: {id_orden}")

        resultado = use_case.execute(id_orden)

        logger.info(f"✅ FIN - Orden obtenida exitosamente")
        logger.info("=" * 80)
        print(f"✅ FIN - Orden obtenida exitosamente")
        print("=" * 80)

        return resultado

    except Exception as e:
        logger.error(f"❌ ERROR en get_order: {e}")
        logger.error(f"Tipo de error: {type(e)}")
        import traceback
        logger.error(traceback.format_exc())
        print(f"❌ ERROR en get_order: {e}")
        raise


@router.put("/actualizar")
async def update_order(
    request: ActualizarOrdenCompraRequest,
    use_case: ActualizarOrdenCompra = Depends(get_update_purchase_order_use_case)
):
    """
    Actualiza una orden de compra existente.

    Este endpoint:
    1. Actualiza los campos básicos de la orden (moneda, pago, entrega)
    2. Procesa los productos:
       - Productos con idOcDetalle y eliminar=true: Se eliminan
       - Productos con idOcDetalle y eliminar=false: Se actualizan
       - Productos sin idOcDetalle: Se crean nuevos
    3. Regenera el Excel con los datos actualizados
    4. Elimina el archivo anterior de S3
    5. Sube el nuevo Excel a S3
    6. Actualiza la ruta S3 en la BD

    Args:
        request (ActualizarOrdenCompraRequest): Datos de la orden a actualizar

    Returns:
        dict: Resultado de la operación con status, mensaje y nueva URL
    """
    try:
        logger.info("=" * 80)
        logger.info(f"🔄 INICIO - Actualización de orden de compra ID: {request.idOrden}")
        print("=" * 80)
        print(f"🔄 INICIO - Actualización de orden de compra ID: {request.idOrden}")

        resultado = await use_case.execute(request)

        logger.info(f"✅ FIN - Orden actualizada exitosamente")
        logger.info("=" * 80)
        print(f"✅ FIN - Orden actualizada exitosamente")
        print("=" * 80)

        return resultado

    except Exception as e:
        logger.error(f"❌ ERROR en update_order: {e}")
        logger.error(f"Tipo de error: {type(e)}")
        import traceback
        logger.error(traceback.format_exc())
        print(f"❌ ERROR en update_order: {e}")
        raise


@router.delete("/{id_orden}")
async def delete_order(
    id_orden: int,
    use_case: EliminarOrdenCompra = Depends(get_delete_purchase_order_use_case)
):
    """
    Elimina una orden de compra por su ID.

    Este endpoint:
    1. Obtiene la orden de compra por su ID
    2. Elimina el archivo asociado de S3 (si existe)
    3. Elimina la orden de compra y sus detalles de la base de datos

    Args:
        id_orden (int): ID de la orden de compra a eliminar

    Returns:
        dict: Resultado de la operación con status y mensaje
    """
    try:
        logger.info("=" * 80)
        logger.info(f"🗑️ INICIO - Eliminación de orden de compra ID: {id_orden}")
        print("=" * 80)
        print(f"🗑️ INICIO - Eliminación de orden de compra ID: {id_orden}")

        resultado = use_case.execute(id_orden)

        logger.info(f"✅ FIN - Orden eliminada exitosamente")
        logger.info("=" * 80)
        print(f"✅ FIN - Orden eliminada exitosamente")
        print("=" * 80)

        return resultado

    except Exception as e:
        logger.error(f"❌ ERROR en delete_order: {e}")
        logger.error(f"Tipo de error: {type(e)}")
        import traceback
        logger.error(traceback.format_exc())
        print(f"❌ ERROR en delete_order: {e}")
        raise

