from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.adapters.outbound.database.repositories.ordenes_compra_repository import OrdenesCompraRepository
from app.config.database import get_db
from app.adapters.inbound.api.schemas.generar_oc_schemas import GenerarOCRequest, GenerarOCResponse, ErrorResponse, ProductoOCData
from app.adapters.outbound.database.models.cotizacion_model import CotizacionModel
from app.adapters.outbound.database.models.cotizaciones_versiones_model import CotizacionesVersionesModel
from app.adapters.outbound.database.models.proveedor_contacto_model import ProveedorContactosModel
from app.shared.serializers.generator_oc.generador import Generador
from datetime import datetime
import os
from app.adapters.outbound.external_services.aws.upload_file_to_s3 import upload_file_to_s3

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

    # Inicializar el repositorio de órdenes de compra
    ordenes_repo = OrdenesCompraRepository(db)
    
    # Ejecutar la consulta
    resultados = ordenes_repo.obtener_info_oc(request)
    
    if not resultados:
        raise HTTPException(
            status_code=404, 
            detail="No se encontraron datos para los parámetros especificados"
        )

    print(f"Total de resultados obtenidos: {len(resultados)}")
    ##print(f"Primer resultado: {resultados[0] if resultados else 'No hay resultados'}")

    # Procesar cada contacto de proveedor y generar Excel
    archivos_generados = []
    output_folder = "excels"
    for id_contacto in request.id_contacto_proveedor:
        print(f"========== Procesando contacto número: {id_contacto} ========== ")
        # Generar el siguiente número de orden de compra
        numero_oc = ordenes_repo.generar_siguiente_numero_oc()
        if not numero_oc:
            raise HTTPException(
                status_code=500,
                detail="Error al generar número de orden de compra"
        )
        print(f"Número de orden generado: {numero_oc}")
        # Filtrar los resultados para este contacto específico
        resultados_contacto = [r for r in resultados if r.IDPROVEEDORCONTACTO == id_contacto]
        if resultados_contacto:
            # Obtener el nombre del proveedor del primer resultado
            nombre_proveedor = resultados_contacto[0].PROVEEDOR if resultados_contacto[0].PROVEEDOR else "Proveedor"
            igv = resultados_contacto[0].IGV if resultados_contacto[0].IGV else "SIN IGV"
            #print(f"Nombre del proveedor: {nombre_proveedor}")
            # Convertir los resultados a diccionarios para el generador
            datos_para_excel = []
            for resultado in resultados_contacto:
                datos_para_excel.append({
                    'CANT': resultado.CANT,
                    'UMED': resultado.UMED,
                    'PRODUCTO': resultado.PRODUCTO,
                    'MARCA': resultado.MARCA,
                    'MODELO': resultado.MODELO,
                    'P.UNIT': resultado.PUNIT,
                    'PROVEEDOR': resultado.PROVEEDOR,
                    'PERSONAL': resultado.PERSONAL,
                    'CELULAR': resultado.CELULAR,
                    'CORREO': resultado.CORREO,
                    'DIRECCION': resultado.DIRECCION,
                    'FECHA': resultado.FECHA,
                    'MONEDA': resultado.MONEDA,
                    'PAGO': resultado.PAGO
                })
            #print(f"Datos convertidos para Excel: {len(datos_para_excel)} registros")
            try:
                generador = Generador(
                    num_orden=numero_oc,
                    oc=datos_para_excel,
                    proveedor=nombre_proveedor,
                    igv=igv,
                    output_folder=output_folder
                )
                generador.generar_excel()
                local_path = os.path.join(output_folder, generador.output_file)
                s3_key = f"ordenes_de_compra/{generador.output_file}"
                url = upload_file_to_s3(
                    local_path,
                    s3_key,
                    'bucketcorpe',  # Nombre del bucket
                    'us-east-1'     # Región de AWS
                )
                print(f"URL del archivo subido: {url}")
                archivos_generados.append(url)
                print(f"Excel subido exitosamente a S3 para el contacto {id_contacto}")
                nueva_orden = ordenes_repo.crear_orden_compra({
                    'id_usuario': request.id_usuario,
                    'id_cotizacion': request.id_cotizacion,
                    'version': request.id_version,
                    'correlative': numero_oc,
                    'ruta_s3': url
                })
                print(f"Orden de compra creada: {nueva_orden.ruta_s3}")
            except Exception as e:
                print(f"Error al generar/subir Excel para contacto {id_contacto}: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"No se encontraron productos para el contacto {id_contacto}")

    return GenerarOCResponse(
        message=f"OC generada correctamente. Archivos subidos: {', '.join(archivos_generados)}",
        datos=archivos_generados,
        total_registros=len(archivos_generados)
    )






