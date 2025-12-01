from fastapi import APIRouter, Query, HTTPException
from app.adapters.inbound.api.schemas.ordenes_compra_schemas import (
    OrdenesCompraRequest,
    ActualizarOrdenCompraRequest,
    OrdenCompraDetalleResponse
)
from app.adapters.inbound.api.schemas.ordenes_compra_auditoria_schemas import (
    ListarAuditoriasResponse
)
from app.core.use_cases.generar_oc.generar_orden_compra import GenerarOrdenCompra
from app.core.use_cases.generar_oc.eliminar_orden_compra import EliminarOrdenCompra
from app.core.use_cases.generar_oc.actualizar_orden_compra import ActualizarOrdenCompra
from app.core.use_cases.generar_oc.obtener_orden_compra import ObtenerOrdenCompra
from app.core.use_cases.generar_oc.listar_auditoria_orden_compra import ListarAuditoriaOrdenCompra
from fastapi import Depends
from app.dependencies import (
    get_generate_purchase_order_use_case,
    get_delete_purchase_order_use_case,
    get_update_purchase_order_use_case,
    get_obtener_purchase_order_use_case,
    get_listar_auditoria_orden_compra_use_case
)
from app.core.domain.exceptions import (
    OrdenCompraError,
    OrdenCompraNotFoundError,
    ProductosSinRelacionError,
    VersionCotizacionNotFoundError,
    DatosInsuficientesError,
    GeneracionExcelError,
    AlmacenamientoError,
    ActualizacionOrdenError,
    EliminacionOrdenError,
)
from typing import Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ordenes-compra", tags=["Ordenes de Compra"])


def _log_inicio(mensaje: str):
    """Helper privado para logging de inicio de operaciones"""
    logger.info("=" * 80)
    logger.info(mensaje)
    print("=" * 80)
    print(mensaje)


def _log_fin(mensaje: str):
    """Helper privado para logging de fin de operaciones"""
    logger.info(mensaje)
    logger.info("=" * 80)
    print(mensaje)
    print("=" * 80)


def _log_error(operacion: str, error: Exception):
    """Helper privado para logging de errores"""
    logger.error(f"❌ ERROR en {operacion}: {error}")
    logger.error(f"Tipo de error: {type(error)}")
    import traceback
    logger.error(traceback.format_exc())
    print(f"❌ ERROR en {operacion}: {error}")


@router.post("/generar")
async def create_order(order: OrdenesCompraRequest, use_case: GenerarOrdenCompra = Depends(get_generate_purchase_order_use_case)):
    """
    Crea nuevas órdenes de compra.

    Este endpoint:
    1. Valida la versión de cotización
    2. Valida que los productos tengan relación con cotización
    3. Guarda las órdenes en BD
    4. Genera archivos Excel
    5. Sube a S3
    6. Confirma transacción y dispara eventos

    Args:
        order: Datos de las órdenes a crear

    Returns:
        dict: Status y URLs de los archivos generados

    Raises:
        HTTPException 400: Error de validación (productos sin relación, versión inexistente)
        HTTPException 404: No hay datos para generar órdenes
        HTTPException 500: Error de infraestructura (Excel, S3)
        HTTPException 503: Servicio de almacenamiento no disponible
    """
    try:
        _log_inicio("🚀 INICIO - Creación de órdenes de compra")
        logger.info(f"📦 Request: {len(order.data)} órdenes a procesar")
        print(f"📦 Request: {len(order.data)} órdenes a procesar")

        urls = await use_case.execute(order)

        _log_fin(f"✅ FIN - {len(urls)} URLs generadas")
        return {"status": "Órdenes de compra generadas", "urls": urls}

    except ProductosSinRelacionError as e:
        _log_error("create_order", e)
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except VersionCotizacionNotFoundError as e:
        _log_error("create_order", e)
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except DatosInsuficientesError as e:
        _log_error("create_order", e)
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except AlmacenamientoError as e:
        _log_error("create_order", e)
        raise HTTPException(
            status_code=503,
            detail=f"Servicio de almacenamiento no disponible: {str(e)}"
        )
    except (GeneracionExcelError, OrdenCompraError) as e:
        _log_error("create_order", e)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    except Exception as e:
        _log_error("create_order", e)
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado: {str(e)}"
        )


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
        :param id_orden:
        :param use_case:
    """
    try:
        _log_inicio(f"📋 INICIO - Obtención de orden de compra ID: {id_orden}")
        resultado = use_case.execute(id_orden)
        _log_fin("✅ FIN - Orden obtenida exitosamente")
        return resultado

    except OrdenCompraNotFoundError as e:
        _log_error("get_order", e)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        _log_error("get_order", e)
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")


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
        :param request:
        :param use_case:
    """
    try:
        _log_inicio(f"🔄 INICIO - Actualización de orden de compra ID: {request.idOrden}")
        logger.info(f"📦 Request recibido: idOrden={request.idOrden}, productos={len(request.productos)}")
        resultado = await use_case.execute(request)
        _log_fin("✅ FIN - Orden actualizada exitosamente")
        return resultado

    except OrdenCompraNotFoundError as e:
        _log_error("update_order", e)
        raise HTTPException(status_code=404, detail=str(e))
    except ActualizacionOrdenError as e:
        _log_error("update_order", e)
        raise HTTPException(status_code=400, detail=str(e))
    except GeneracionExcelError as e:
        _log_error("update_order", e)
        raise HTTPException(status_code=500, detail=str(e))
    except AlmacenamientoError as e:
        _log_error("update_order", e)
        raise HTTPException(status_code=503, detail=f"Servicio de almacenamiento no disponible: {str(e)}")
    except Exception as e:
        _log_error("update_order", e)
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")


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
        :param id_orden:
        :param use_case:
    """
    try:
        _log_inicio(f"🗑️ INICIO - Eliminación de orden de compra ID: {id_orden}")
        resultado = use_case.execute(id_orden)
        _log_fin("✅ FIN - Orden eliminada exitosamente")
        return resultado

    except OrdenCompraNotFoundError as e:
        _log_error("delete_order", e)
        raise HTTPException(status_code=404, detail=str(e))
    except AlmacenamientoError as e:
        _log_error("delete_order", e)
        raise HTTPException(status_code=503, detail=f"Servicio de almacenamiento no disponible: {str(e)}")
    except EliminacionOrdenError as e:
        _log_error("delete_order", e)
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        _log_error("delete_order", e)
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")


@router.get("/auditoria/logs", response_model=ListarAuditoriasResponse)
def get_auditoria_logs(
    id_orden_compra: Optional[int] = Query(None, description="Filtrar por ID de orden de compra"),
    numero_oc: Optional[str] = Query(None, description="Filtrar por número de OC (correlativo) - búsqueda parcial"),
    tipo_operacion: Optional[str] = Query(None, description="Filtrar por tipo de operación (CREACION, ACTUALIZACION, ELIMINACION)"),
    usuario: Optional[str] = Query(None, description="Buscar por nombre del usuario - búsqueda parcial"),
    proveedor: Optional[str] = Query(None, description="Buscar por razón social del proveedor - búsqueda parcial"),
    ruc_proveedor: Optional[str] = Query(None, description="Filtrar por RUC del proveedor"),
    contacto: Optional[str] = Query(None, description="Buscar por nombre del contacto - búsqueda parcial"),
    fecha_desde: Optional[datetime] = Query(None, description="Filtrar desde esta fecha (formato: YYYY-MM-DD)"),
    fecha_hasta: Optional[datetime] = Query(None, description="Filtrar hasta esta fecha (formato: YYYY-MM-DD)"),
    page: int = Query(1, description="Número de página", ge=1),
    page_size: int = Query(10, description="Cantidad de registros por página", ge=1, le=100),
    use_case: ListarAuditoriaOrdenCompra = Depends(get_listar_auditoria_orden_compra_use_case)
):
    """
    Obtiene el historial de auditoría de órdenes de compra.

    Este endpoint retorna:
    - Historial completo de cambios (creación, actualización, eliminación)
    - Cambios en proveedor y contacto (antiguo → nuevo)
    - Cambios en productos (agregados, modificados, eliminados)
    - Cambios en montos
    - Descripción legible de cada cambio

    Filtros disponibles:
    - id_orden_compra: Filtrar por una orden específica
    - numero_oc: Buscar por número de OC/correlativo (búsqueda parcial)
    - tipo_operacion: Filtrar por tipo (CREACION, ACTUALIZACION, ELIMINACION)
    - id_usuario: Filtrar por usuario que realizó el cambio
    - proveedor: Buscar por razón social del proveedor (búsqueda parcial)
    - ruc_proveedor: Filtrar por RUC exacto del proveedor
    - contacto: Buscar por nombre del contacto (búsqueda parcial)
    - fecha_desde/fecha_hasta: Rango de fechas

    Paginación:
    - page: Número de página (default: 1)
    - page_size: Cantidad de registros por página (default: 10, max: 100)

    Returns:
        ListarAuditoriasResponse: Lista de auditorías con metadatos de paginación

    Examples:
        GET /ordenes-compra/auditoria/logs
        GET /ordenes-compra/auditoria/logs?page=2&page_size=20
        GET /ordenes-compra/auditoria/logs?id_orden_compra=123
        GET /ordenes-compra/auditoria/logs?numero_oc=OC-0001
        GET /ordenes-compra/auditoria/logs?tipo_operacion=ACTUALIZACION
        GET /ordenes-compra/auditoria/logs?proveedor=EQUIPAMIENTOS
        GET /ordenes-compra/auditoria/logs?ruc_proveedor=20601580820
        GET /ordenes-compra/auditoria/logs?contacto=Juan
        GET /ordenes-compra/auditoria/logs?fecha_desde=2025-01-01&fecha_hasta=2025-12-31
        GET /ordenes-compra/auditoria/logs?proveedor=GRUPO&tipo_operacion=CREACION&page=1&page_size=10
    """
    try:
        _log_inicio("📋 INICIO - Listado de auditorías de órdenes de compra")
        logger.info(f"Filtros: id_orden={id_orden_compra}, numero_oc={numero_oc}, tipo={tipo_operacion}, "
                   f"usuario={usuario}, proveedor={proveedor}, ruc={ruc_proveedor}, contacto={contacto}, "
                   f"página={page}, tamaño={page_size}")

        resultado = use_case.execute(
            id_orden_compra=id_orden_compra,
            numero_oc=numero_oc,
            tipo_operacion=tipo_operacion,
            usuario=usuario,
            proveedor=proveedor,
            ruc_proveedor=ruc_proveedor,
            contacto=contacto,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            page=page,
            page_size=page_size
        )

        _log_fin(f"✅ FIN - Página {resultado['page']}/{resultado['total_pages']} - "
                f"{len(resultado['items'])} auditorías retornadas de {resultado['total']} totales")
        return resultado
    except Exception as e:
        _log_error("get_auditoria_logs", e)
        raise

