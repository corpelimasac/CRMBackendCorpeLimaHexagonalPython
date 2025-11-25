import asyncio
import logging
from typing import List

from fastapi import HTTPException

from app.adapters.inbound.api.schemas.generar_oc_schemas import GenerarOCRequest
from app.adapters.inbound.api.schemas.ordenes_compra_schemas import OrdenesCompraRequest
from app.core.domain.entities.ordenes_compra import OrdenesCompra, OrdenesCompraItem
from app.core.ports.repositories.cotizaciones_versiones_repository import CotizacionVersionesRepositoryPort
from app.core.ports.repositories.ordenes_compra_repository import OrdenesCompraRepositoryPort
from app.core.ports.services.file_storage_port import FileStoragePort
from app.core.ports.services.generator_excel_port import ExcelGeneratorPort

logger = logging.getLogger(__name__)

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

    async def _process_and_generate_excel_for_contacto_sin_commit(
            self, id_contacto: int,
            generar_oc_request: GenerarOCRequest
    ) -> dict:
        """
        Procesa un contacto específico, genera el Excel y lo sube a S3.
        NO actualiza la BD (eso se hace después de que todo salga bien).
        Esta función está diseñada para ser ejecutada de manera asíncrona.

        Returns:
            dict: {'url': str, 'orden_ids': List[int]}
        """
        try:
            logger.info(f"Procesando contacto {id_contacto}")

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
                raise ValueError(f"No se generaron archivos Excel para el contacto {id_contacto}")

            # Subir archivos a S3
            urls = await self.file_storage.save_multiple(excel_files)

            if not urls:
                raise ValueError(f"No se pudo subir a S3 para el contacto {id_contacto}")

            url_s3 = urls[0]
            logger.info(f"Excel generado y subido exitosamente para el contacto {id_contacto}: {url_s3}")

            # Obtener las órdenes de compra asociadas a este contacto
            ordenes = self.ordenes_compra_repo.obtener_ordenes_por_contacto_y_version(
                generar_oc_request.id_cotizacion,
                generar_oc_request.id_version,
                id_contacto
            )

            orden_ids = [orden.id_orden for orden in ordenes]
            logger.debug(f"Órdenes encontradas para contacto {id_contacto}: {orden_ids}")

            return {
                'url': url_s3,
                'orden_ids': orden_ids
            }

        except Exception as e:
            logger.error(f"Error al procesar el contacto {id_contacto}: {e}", exc_info=True)
            raise

    async def execute(self, request: OrdenesCompraRequest) -> List[str]:
        logger.info("Ejecutando caso de uso GenerarOrdenCompra")

        if not self.cotizacion_version_repo.exists_by_id(request.idCotizacionVersiones):
            raise ValueError("La versión de cotización especificada no existe.")

        logger.info(f"Versión de cotización {request.idCotizacionVersiones} verificada")

        # 1. Preparar todas las órdenes de compra
        # IMPORTANTE: NO uniformizar aquí, guardar los datos tal como vienen del frontend
        logger.info(f"Preparando {len(request.data)} órdenes de compra...")
        ordenes_a_guardar = []

        for order_data in request.data:
            # Validar que todos los productos tengan id_producto_cotizacion
            productos_sin_id = [
                producto.idProducto
                for producto in order_data.productos
                if producto.idProductoCotizacion is None
            ]

            if productos_sin_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error: Los siguientes productos no tienen id_producto_cotizacion: {productos_sin_id}. "
                           f"Este campo es obligatorio para relacionar los productos con la cotización."
                )

            # Mapear los productos del DTO a la entidad OrdenesCompraItem
            # Guardar los productos tal como vienen del frontend (sin uniformizar)
            items_entidad = [
                OrdenesCompraItem(
                    id_producto=producto.idProducto,
                    cantidad=producto.cantidad,
                    p_unitario=producto.pUnitario,
                    p_total=producto.ptotal,
                    igv=getattr(producto, 'igv', 'CON IGV'),  # IGV tal como viene del frontend
                    id_producto_cotizacion=producto.idProductoCotizacion  # Relacionar con productos_cotizaciones
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
                igv=order_data.igv,
                total=order_data.total,
                moneda=order_data.proveedorInfo.moneda,
                pago=order_data.proveedorInfo.pago,
                entrega=order_data.proveedorInfo.entrega,
                items=items_entidad,
                consorcio=request.consorcio
            )

            ordenes_a_guardar.append(ordenes_compra_entity)

        # PASO 2: Guardar órdenes SIN COMMIT (solo flush para obtener IDs)
        logger.info(f"Guardando {len(ordenes_a_guardar)} órdenes de compra en batch (sin commit)...")
        orden_ids = self.ordenes_compra_repo.save_batch_sin_commit(ordenes_a_guardar)
        logger.info(f"✅ {len(orden_ids)} órdenes preparadas (pendiente commit)")

        # PASO 3: Crear GenerarOCRequest con todos los contactos
        lista_ids_contacto = list(set([
            order_data.proveedorInfo.idProveedorContacto
            for order_data in request.data
        ]))
        logger.debug(f"Lista de IDs de contacto: {lista_ids_contacto}")

        generar_oc_request = GenerarOCRequest(
            id_usuario=request.idUsuario,
            id_cotizacion=request.idCotizacion,
            id_version=request.idCotizacionVersiones,
            id_contacto_proveedor=lista_ids_contacto,
            consorcio=request.consorcio
        )

        # PASO 4: Verificar que hay datos para generar Excel
        resultados = self.ordenes_compra_repo.obtener_info_oc(generar_oc_request)
        if not resultados:
            self.ordenes_compra_repo.rollback()
            raise HTTPException(
                status_code=404,
                detail="No se encontraron datos para los parámetros especificados"
            )

        logger.info(f"Total de resultados obtenidos: {len(resultados)}")

        # PASO 5: Generar Excel y subir a S3 usando paralelismo
        logger.info("Generando Excel y subiendo a S3 con paralelismo...")
        try:
            generated_files_urls = []

            # Usar asyncio.gather para paralelismo asíncrono
            tasks = [
                self._process_and_generate_excel_for_contacto_sin_commit(id_contacto, generar_oc_request)
                for id_contacto in lista_ids_contacto
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Verificar resultados
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"❌ Error en procesamiento paralelo: {result}")
                    raise result
                elif isinstance(result, dict) and result.get('url'):
                    generated_files_urls.append(result['url'])
                    # Actualizar URLs en memoria (sin commit)
                    for orden_id in result.get('orden_ids', []):
                        self.ordenes_compra_repo.actualizar_ruta_s3_sin_commit(orden_id, result['url'])

            if not generated_files_urls:
                self.ordenes_compra_repo.rollback()
                raise HTTPException(
                    status_code=500,
                    detail="No se pudo generar ninguna orden de compra."
                )

            # PASO 6: TODO salió bien → COMMIT ÚNICO con evento
            logger.info("✅ Todos los archivos subidos exitosamente. Haciendo commit...")
            self.ordenes_compra_repo.commit_con_evento(ordenes_a_guardar)

            logger.info(f"✅ {len(generated_files_urls)} órdenes creadas con éxito - Evento en background")
            return generated_files_urls

        except Exception as e:
            logger.error(f"❌ Error durante generación/subida: {e}. Haciendo rollback...", exc_info=True)
            self.ordenes_compra_repo.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error al crear órdenes de compra: {str(e)}"
            )