from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import case, text
from app.adapters.outbound.database.models.cotizacion_model import CotizacionModel
from app.adapters.outbound.database.models.cotizaciones_versiones_model import CotizacionesVersionesModel
from app.adapters.outbound.database.models.productos_cotizaciones_model import ProductosCotizacionesModel
from app.adapters.outbound.database.models.productos_model import ProductosModel
from app.adapters.outbound.database.models.unidad_medida_model import UnidadMedidaModel
from app.adapters.outbound.database.models.marcas_model import MarcasModel
from app.adapters.outbound.database.models.proveedores_model import ProveedoresModel
from app.adapters.outbound.database.models.proveedor_contacto_model import ProveedorContactosModel
from app.adapters.outbound.database.models.proveedor_detalle_model import ProveedorDetalleModel
from app.adapters.outbound.database.models.intermedia_proveedor_contacto_model import intermedia_proveedor_contacto
from app.config.database import get_db
from app.adapters.inbound.api.schemas.generar_oc_schemas import GenerarOCRequest, GenerarOCResponse, ErrorResponse, ProductoOCData

# Configuración de la API
router = APIRouter(
    prefix="/generar-oc", 
    tags=["Generar OC"],
    responses={
        404: {"model": ErrorResponse, "description": "Recurso no encontrado"},
        422: {"model": ErrorResponse, "description": "Error de validación"},
        500: {"model": ErrorResponse, "description": "Error interno del servidor"}
    },
)

@router.post(
    "/", 
    summary="Generar Orden de Compra",
    description="Genera una orden de compra basada en una cotización específica, versión y contacto de proveedor",
    response_model=GenerarOCResponse,
    status_code=200
)
async def generar_orden_compra(
    request: GenerarOCRequest, 
    db: Session = Depends(get_db)
) -> GenerarOCResponse:
    """
    Genera una orden de compra con los siguientes parámetros:
    
    - **id_cotizacion**: ID de la cotización
    - **id_version**: ID de la versión de la cotización  
    - **id_contacto_proveedor**: ID del contacto del proveedor
    
    Retorna los datos completos de la orden de compra incluyendo:
    - Información de productos
    - Datos del proveedor
    - Información de contacto
    - Precios y condiciones
    """
    
    # Verificar que la cotización existe
    cotizacion = db.query(CotizacionModel).filter(
        CotizacionModel.id_cotizacion == request.id_cotizacion
    ).first()
    if not cotizacion:
        raise HTTPException(
            status_code=404, 
            detail=f"Cotización con ID {request.id_cotizacion} no encontrada"
        )
    
    # Verificar que la versión existe
    version = db.query(CotizacionesVersionesModel).filter(
        CotizacionesVersionesModel.id_cotizacion_versiones == request.id_version,
        CotizacionesVersionesModel.id_cotizacion == request.id_cotizacion
    ).first()
    if not version:
        raise HTTPException(
            status_code=404, 
            detail=f"Versión {request.id_version} de la cotización {request.id_cotizacion} no encontrada"
        )
    
    # Verificar que los contactos del proveedor existen
    for id_contacto in request.id_contacto_proveedor:
        contacto_proveedor = db.query(ProveedorContactosModel).filter(
            ProveedorContactosModel.id_proveedor_contacto == id_contacto
        ).first()
        if not contacto_proveedor:
            raise HTTPException(
                status_code=404, 
                detail=f"Contacto de proveedor con ID {id_contacto} no encontrado"
            )
    


    query = db.query(
        CotizacionesVersionesModel.id_cotizacion.label('IDCOTIZACION'),
        CotizacionesVersionesModel.id_cotizacion_versiones.label('IDVERSION'),
        ProductosCotizacionesModel.cantidad.label('CANT'),
        UnidadMedidaModel.descripcion.label('UMED'),
        ProductosModel.nombre.label('PRODUCTO'),
        MarcasModel.nombre.label('MARCA'),
        ProductosModel.modelo_marca.label('MODELO'),
        CotizacionesVersionesModel.fecha_modificacion.label('FECHA'),
        ProveedoresModel.id_proveedor.label('IDPROVEEDOR'),
        ProveedoresModel.razon_social.label('PROVEEDOR'),
        ProveedorContactosModel.id_proveedor_contacto.label('IDPROVEEDORCONTACTO'),
        ProveedorContactosModel.nombre.label('PERSONAL'),
        ProveedorContactosModel.telefono.label('TELEFONO'),
        ProveedorContactosModel.celular.label('CELULAR'),
        ProveedorContactosModel.correo.label('CORREO'),
        ProveedoresModel.direccion.label('DIRECCION'),
        case(
            (ProveedorDetalleModel.moneda == 'S/.', 'SOLES'),
            else_='DOLARES'
        ).label('MONEDA'),
        ProveedoresModel.condiciones_pago.label('PAGO'),
        ProveedorDetalleModel.precio_costo_unitario.label('PUNIT'),
        ProveedorDetalleModel.igv.label('IGV')
    ).select_from(CotizacionesVersionesModel)\
     .join(ProductosCotizacionesModel, CotizacionesVersionesModel.id_cotizacion_versiones == ProductosCotizacionesModel.id_cotizacion_versiones)\
     .join(ProductosModel, ProductosCotizacionesModel.id_producto == ProductosModel.id_producto)\
     .join(UnidadMedidaModel, ProductosModel.id_unidad_medida == UnidadMedidaModel.id_unidad_medida)\
     .join(MarcasModel, ProductosModel.id_marca == MarcasModel.id_marca)\
     .join(ProveedoresModel, ProductosModel.id_proveedor == ProveedoresModel.id_proveedor)\
     .join(intermedia_proveedor_contacto, ProveedoresModel.id_proveedor == intermedia_proveedor_contacto.c.id_proveedor)\
     .join(ProveedorContactosModel, intermedia_proveedor_contacto.c.id_proveedor_contacto == ProveedorContactosModel.id_proveedor_contacto)\
     .join(ProveedorDetalleModel, ProductosModel.id_producto == ProveedorDetalleModel.id_producto)\
     .filter(CotizacionesVersionesModel.id_cotizacion == request.id_cotizacion)\
     .filter(ProductosCotizacionesModel.id_cotizacion_versiones == request.id_version)\
     .filter(ProveedorContactosModel.id_proveedor_contacto.in_(request.id_contacto_proveedor))

        # Ejecutar la consulta
    resultados = query.all()

    if not resultados:
        raise HTTPException(
            status_code=404, 
            detail="No se encontraron datos para los parámetros especificados"
        )
    
# Imprimir el resultado por cada contacto de proveedor
    for id_contacto in request.id_contacto_proveedor:
        print(f"========== Resultado del contacto número: {id_contacto} ========== ")
    
    # Filtrar los resultados para este contacto específico
        resultados_contacto = [r for r in resultados if r.IDPROVEEDORCONTACTO == id_contacto]
    
    # Imprimir los resultados filtrados
        for resultado in resultados_contacto:
            print(resultado)



    return GenerarOCResponse(
        message="OC generada correctamente",
        datos=[],
        total_registros=0
    )






