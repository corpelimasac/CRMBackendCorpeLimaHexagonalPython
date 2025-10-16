from app.core.domain.entities.ordenes_compra import OrdenesCompra, OrdenesCompraItem # ... y otros
from app.core.ports.repositories.ordenes_compra_repository import OrdenesCompraRepositoryPort
from app.core.ports.repositories.cotizaciones_versiones_repository import CotizacionVersionesRepositoryPort
from app.core.ports.services.generator_excel_port import ExcelGeneratorPort
from app.core.ports.services.file_storage_port import FileStoragePort
from app.adapters.inbound.api.schemas.ordenes_compra_schemas import OrdenesCompraRequest
from app.adapters.inbound.api.schemas.generar_oc_schemas import GenerarOCRequest
from typing import List
from fastapi import HTTPException
import asyncio

import traceback

class GenerarOrdenCompra:   
    def __init__(
        self,
        ordenes_compra_repo: OrdenesCompraRepositoryPort,
        cotizacion_version_repo: CotizacionVersionesRepositoryPort,
        excel_generator: ExcelGeneratorPort,
        file_storage: FileStoragePort
    ):
        self.ordenes_compra_repo = ordenes_compra_repo
        self.cotizacion_version_repo = cotizacion_version_repo
        self.excel_generator = excel_generator
        self.file_storage = file_storage

    async def _process_and_generate_excel_for_contacto(
            self, id_contacto: int,
            generar_oc_request: GenerarOCRequest
    ) -> str | None:
        """
        Procesa un contacto específico, genera el Excel, lo sube a S3 y actualiza la URL en la BD.
        Esta función está diseñada para ser ejecutada de manera asíncrona.
        """
        try:
            print(f"Procesando contacto {id_contacto}")
            
            # Crear un request específico para este contacto
            request_contacto = GenerarOCRequest(
                id_usuario=generar_oc_request.id_usuario,
                id_cotizacion=generar_oc_request.id_cotizacion,
                id_version=generar_oc_request.id_version,
                id_contacto_proveedor=[id_contacto],
                consorcio=generar_oc_request.consorcio
            )
            
            # Generar Excel para este contacto específico
            excel_files = self.excel_generator.generate_for_order(request_contacto)
            
            if not excel_files:
                print(f"No se generaron archivos Excel para el contacto {id_contacto}")
                return None
                
            # Subir archivos a S3
            urls = await self.file_storage.save_multiple(excel_files)
            
            if urls:
                url_s3 = urls[0]
                print(f"Excel generado y subido exitosamente para el contacto {id_contacto}: {url_s3}")
                
                # Obtener las órdenes de compra asociadas a este contacto
                ordenes = self.ordenes_compra_repo.obtener_ordenes_por_contacto_y_version(
                    generar_oc_request.id_cotizacion,
                    generar_oc_request.id_version,
                    id_contacto
                )
                
                # Actualizar la URL S3 en todas las órdenes de este contacto
                for orden in ordenes:
                    exito = self.ordenes_compra_repo.actualizar_ruta_s3(orden.id_orden, url_s3)
                    if exito:
                        print(f"URL S3 actualizada en BD para orden {orden.id_orden}")
                    else:
                        print(f"Error al actualizar URL S3 para orden {orden.id_orden}")
                
                return url_s3
            
            return None
            
        except Exception as e:
            print(f"Error al procesar el contacto {id_contacto}: {e}")
            traceback.print_exc()
            return None

    async def execute(self, request: OrdenesCompraRequest) -> List[str]:
        print("Ejecutando caso de uso")

        if not self.cotizacion_version_repo.exists_by_id(request.idCotizacionVersiones):
            raise ValueError("La versión de cotización especificada no existe.")
    
        print("Version de cotización existe")

        # 1. Preparar todas las órdenes de compra
        print("Preparando órdenes de compra...")
        ordenes_a_guardar = []
        
        for order_data in request.data:
            # Mapear los productos del DTO a la entidad OrdenesCompraItem
            items_entidad = [
                OrdenesCompraItem(
                    id_producto=producto.idProducto,
                    cantidad=producto.cantidad,
                    p_unitario=producto.pUnitario,
                    p_total=producto.ptotal
                )
                for producto in order_data.productos
            ]

            # Mapear DTO completo a la Entidad de Dominio OrdenesCompra
            ordenes_compra_entity = OrdenesCompra(
                id_usuario=request.idUsuario,
                id_cotizacion=request.idCotizacion,
                id_cotizacion_versiones=request.idCotizacionVersiones,
                id_proveedor=order_data.proveedorInfo.idProveedor,
                id_proveedor_contacto=order_data.proveedorInfo.idProveedorContacto,
                moneda=order_data.proveedorInfo.moneda,
                pago=order_data.proveedorInfo.pago,
                entrega=order_data.proveedorInfo.entrega,
                items=items_entidad,
                consorcio=request.consorcio
            )
            
            ordenes_a_guardar.append(ordenes_compra_entity)

        # Guardar TODAS las órdenes en una sola transacción con UN SOLO EVENTO
        print(f"Guardando {len(ordenes_a_guardar)} órdenes de compra en batch...")
        self.ordenes_compra_repo.save_batch(ordenes_a_guardar)
        print(f"✅ {len(ordenes_a_guardar)} órdenes guardadas exitosamente")

        # 2. Crear GenerarOCRequest con todos los contactos
        lista_ids_contacto = list(set([
            order_data.proveedorInfo.idProveedorContacto
            for order_data in request.data
        ]))
        print(f"Lista de IDs de contacto: {lista_ids_contacto}")

        generar_oc_request = GenerarOCRequest(
            id_usuario=request.idUsuario,
            id_cotizacion=request.idCotizacion,
            id_version=request.idCotizacionVersiones,
            id_contacto_proveedor=lista_ids_contacto,
            consorcio=request.consorcio
        )

        # 3. Verificar que hay datos para generar Excel
        resultados = self.ordenes_compra_repo.obtener_info_oc(generar_oc_request)
        if not resultados:
            raise HTTPException(
                status_code=404, 
                detail="No se encontraron datos para los parámetros especificados"
            )

        print(f"Total de resultados obtenidos: {len(resultados)}")

        # 4. Generar Excel y subir a S3 usando paralelismo
        print("Generando Excel y subiendo a S3 con paralelismo...")
        generated_files_urls = []
        
        # Usar asyncio.gather para paralelismo asíncrono
        tasks = [
            self._process_and_generate_excel_for_contacto(id_contacto, generar_oc_request)
            for id_contacto in lista_ids_contacto
        ]
        
        urls = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrar URLs válidas
        for url in urls:
            if isinstance(url, str) and url:
                generated_files_urls.append(url)
            elif isinstance(url, Exception):
                print(f"Error en procesamiento paralelo: {url}")

        if not generated_files_urls:
            raise HTTPException(
                status_code=500,
                detail="No se pudo generar ninguna orden de compra."
            )

        print(f"Se generaron {len(generated_files_urls)} archivos Excel exitosamente")
        return generated_files_urls