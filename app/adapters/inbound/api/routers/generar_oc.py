from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.adapters.outbound.database.repositories.ordenes_compra_repository import OrdenesCompraRepository
from app.config.database import get_db, SessionLocal
from app.adapters.inbound.api.schemas.generar_oc_schemas import GenerarOCRequest, GenerarOCResponse, ErrorResponse, ProductoOCData
from app.adapters.outbound.database.models.cotizacion_model import CotizacionModel
from app.adapters.outbound.database.models.cotizaciones_versiones_model import CotizacionesVersionesModel
from app.adapters.outbound.database.models.proveedor_contacto_model import ProveedorContactosModel
from app.shared.serializers.generator_oc.generador import Generador
from datetime import datetime
import os
from app.adapters.outbound.external_services.aws.upload_file_to_s3 import upload_file_to_s3
import concurrent.futures
import threading
import traceback

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

def _process_and_generate_oc(
    id_contacto: int,
    resultados: list,
    request: GenerarOCRequest,
    output_folder: str,
    lock: threading.Lock
) -> str | None:
    """
    Procesa los datos de un contacto, genera la OC, la sube a S3 y la guarda en la BD.
    Esta función está diseñada para ser ejecutada en un hilo separado.
    """
    db = None
    try:
        db = SessionLocal()
        ordenes_repo = OrdenesCompraRepository(db)

        # Filtrar los resultados para este contacto específico
        resultados_contacto = [r for r in resultados if r.IDPROVEEDORCONTACTO == id_contacto]
        
        if not resultados_contacto:
            print(f"No se encontraron productos para el contacto {id_contacto}")
            return None

        # Generar el siguiente número de orden de compra de forma segura
        with lock:
            numero_oc = ordenes_repo.generar_siguiente_numero_oc()
        
        if not numero_oc:
            print("Error al generar número de orden de compra")
            return None
        
        print(f"Procesando OC {numero_oc} para el contacto {id_contacto}")

        nombre_proveedor = resultados_contacto[0].PROVEEDOR or "Proveedor"
        igv = resultados_contacto[0].IGV or "SIN IGV"

        datos_para_excel = [
            {
                'CANT': r.CANT, 'UMED': r.UMED, 'PRODUCTO': r.PRODUCTO,
                'MARCA': r.MARCA, 'MODELO': r.MODELO, 'P.UNIT': r.PUNIT,
                'PROVEEDOR': r.PROVEEDOR, 'PERSONAL': r.PERSONAL,
                'CELULAR': r.CELULAR, 'CORREO': r.CORREO,
                'DIRECCION': r.DIRECCION, 'FECHA': r.FECHA,
                'MONEDA': r.MONEDA, 'PAGO': r.PAGO
            } for r in resultados_contacto
        ]

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
        
        url = upload_file_to_s3(local_path, s3_key, 'bucketcorpe', 'us-east-1')
        print(f"URL del archivo subido: {url}")

        ordenes_repo.crear_orden_compra({
            'id_usuario': request.id_usuario,
            'id_cotizacion': request.id_cotizacion,
            'version': request.id_version,
            'correlative': numero_oc,
            'ruta_s3': url
        })

        os.remove(local_path)
        print(f"Excel subido y OC creada exitosamente para el contacto {id_contacto}")
        return url

    except Exception as e:
        print(f"Error al procesar el contacto {id_contacto}: {e}")
        traceback.print_exc()
        return None
    finally:
        if db:
            db.close()

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

    archivos_generados = []
    output_folder = "excels"
    lock = threading.Lock()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_url = {
            executor.submit(
                _process_and_generate_oc,
                id_contacto,
                resultados,
                request,
                output_folder,
                lock
            ): id_contacto for id_contacto in request.id_contacto_proveedor
        }
        for future in concurrent.futures.as_completed(future_to_url):
            url = future.result()
            if url:
                archivos_generados.append(url)

    if not archivos_generados:
        raise HTTPException(
            status_code=500,
            detail="No se pudo generar ninguna orden de compra."
        )

    return GenerarOCResponse(
        message=f"Se generaron {len(archivos_generados)} OCs correctamente.",
        datos=archivos_generados,
        total_registros=len(archivos_generados)
    )






