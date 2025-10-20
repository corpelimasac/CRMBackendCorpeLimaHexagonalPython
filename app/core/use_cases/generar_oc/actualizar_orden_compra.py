import os
import logging
from datetime import datetime
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.ports.repositories.ordenes_compra_repository import OrdenesCompraRepositoryPort
from app.core.ports.services.generator_excel_port import ExcelGeneratorPort
from app.core.ports.services.file_storage_port import FileStoragePort
from app.adapters.outbound.external_services.aws.s3_service import S3Service
from app.adapters.inbound.api.schemas.ordenes_compra_schemas import ActualizarOrdenCompraRequest
from app.core.services.registro_compra_auditoria_service import RegistroCompraAuditoriaService

logger = logging.getLogger(__name__)


class ActualizarOrdenCompra:
    """
    Caso de uso para actualizar una orden de compra.

    Este caso de uso:
    1. Valida que la orden exista
    2. Actualiza los campos básicos de la orden (moneda, pago, entrega)
    3. Procesa los productos:
       - Productos con idOcDetalle y eliminar=true: Se eliminan
       - Productos con idOcDetalle y eliminar=false: Se actualizan
       - Productos sin idOcDetalle: Se crean nuevos (eliminar siempre será false)
    4. Regenera el Excel con los datos actualizados
    5. Elimina el archivo anterior de S3
    6. Sube el nuevo Excel a S3
    7. Actualiza la ruta S3 en la BD

    Arquitectura Hexagonal:
    - Caso de uso en la capa de aplicación
    - Se comunica con puertos (repositories, services)
    - Los adaptadores implementan los puertos
    """

    def __init__(
        self,
        ordenes_compra_repo: OrdenesCompraRepositoryPort,
        excel_generator: ExcelGeneratorPort,
        file_storage: FileStoragePort,
        db: Session,
        s3_service: S3Service = None,
        auditoria_service: Optional[RegistroCompraAuditoriaService] = None
    ):
        """
        Inicializa el caso de uso con las dependencias necesarias.

        Args:
            ordenes_compra_repo: Repositorio de órdenes de compra
            excel_generator: Generador de archivos Excel
            file_storage: Servicio de almacenamiento de archivos
            db: Sesión de base de datos
            s3_service: Servicio de S3 (opcional, se crea uno nuevo si no se proporciona)
            auditoria_service: Servicio de auditoría (opcional, se crea uno nuevo si no se proporciona)
        """
        from app.core.infrastructure.events.event_dispatcher import get_event_dispatcher

        self.ordenes_compra_repo = ordenes_compra_repo
        self.excel_generator = excel_generator
        self.file_storage = file_storage
        self.db = db
        self.s3_service = s3_service or S3Service()
        self.auditoria_service = auditoria_service or RegistroCompraAuditoriaService(db)
        self.bucket = os.getenv('AWS_BUCKET_NAME', 'corpelima-bucket')
        self.event_dispatcher = get_event_dispatcher()

    async def execute(self, request: ActualizarOrdenCompraRequest) -> dict:
        """
        Ejecuta el caso de uso de actualización de orden de compra.

        Args:
            request (ActualizarOrdenCompraRequest): Datos de la orden a actualizar

        Returns:
            dict: Resultado de la operación con status, mensaje y nueva URL del Excel

        Raises:
            HTTPException: Si hay errores durante el proceso
        """
        try:
            logger.info(f"Iniciando actualización de orden de compra ID: {request.idOrden}")

            # 1. Validar que la orden existe (consulta ligera solo para validación)
            orden = self.ordenes_compra_repo.obtener_orden_por_id(request.idOrden)
            if not orden:
                raise HTTPException(
                    status_code=404,
                    detail=f"Orden de compra con ID {request.idOrden} no encontrada"
                )

            logger.info(f"Orden encontrada: {request.numeroOc}")

            # Obtener datos desde el request (ya vienen del frontend desde el GET)
            ruta_s3_antigua = request.rutaS3Antigua
            numero_oc = request.numeroOc
            consorcio = request.consorcio

            # Guardar monto anterior para auditoría
            monto_anterior = float(orden.total) if hasattr(orden, 'total') and orden.total else 0.0
            id_cotizacion = orden.id_cotizacion if hasattr(orden, 'id_cotizacion') else None
            id_cotizacion_versiones = orden.id_cotizacion_versiones if hasattr(orden, 'id_cotizacion_versiones') else None
            id_usuario = orden.id_usuario if hasattr(orden, 'id_usuario') else None

            # 2. Actualizar campos básicos de la orden (SIN COMMIT)
            if request.moneda or request.pago or request.entrega:
                self.ordenes_compra_repo.actualizar_orden(
                    id_orden=request.idOrden,
                    moneda=request.moneda,
                    pago=request.pago,
                    entrega=request.entrega,
                    auto_commit=False  # NO hacer commit todavía
                )
                logger.info("Campos básicos de la orden actualizados")

            # 3. Procesar productos (SIN COMMIT)
            productos_eliminados = 0
            productos_actualizados = 0
            productos_creados = 0

            for producto in request.productos:
                # Caso 1: Producto existente marcado para eliminar
                if producto.idOcDetalle is not None and producto.eliminar:
                    self.ordenes_compra_repo.eliminar_detalle_producto(
                        producto.idOcDetalle,
                        auto_commit=False  # NO hacer commit todavía
                    )
                    productos_eliminados += 1
                    logger.info(f"Producto detalle {producto.idOcDetalle} eliminado")

                # Caso 2: Producto existente a actualizar
                elif producto.idOcDetalle is not None and not producto.eliminar:
                    self.ordenes_compra_repo.actualizar_detalle_producto(
                        id_oc_detalle=producto.idOcDetalle,
                        cantidad=producto.cantidad,
                        precio_unitario=producto.pUnitario,
                        precio_total=producto.ptotal,
                        auto_commit=False  # NO hacer commit todavía
                    )
                    productos_actualizados += 1
                    logger.info(f"Producto detalle {producto.idOcDetalle} actualizado")

                # Caso 3: Producto nuevo (sin idOcDetalle)
                elif producto.idOcDetalle is None:
                    self.ordenes_compra_repo.crear_detalle_producto(
                        id_orden=request.idOrden,
                        id_producto=producto.idProducto,
                        cantidad=producto.cantidad,
                        precio_unitario=producto.pUnitario,
                        precio_total=producto.ptotal,
                        auto_commit=False  # NO hacer commit todavía
                    )
                    productos_creados += 1
                    logger.info(f"Nuevo producto {producto.idProducto} creado en la orden")

            logger.info(f"Resumen de productos: {productos_eliminados} eliminados, "
                       f"{productos_actualizados} actualizados, {productos_creados} creados")

            # 4. Calcular el nuevo total de la orden
            detalles_actuales = self.ordenes_compra_repo.obtener_detalles_orden(request.idOrden)
            total_orden = sum(detalle.precio_total for detalle in detalles_actuales)
            monto_nuevo = float(total_orden)

            # Actualizar el total en la orden (SIN COMMIT - usamos la misma sesión self.db)
            from app.adapters.outbound.database.models.ordenes_compra_model import OrdenesCompraModel
            self.db.query(OrdenesCompraModel).filter(
                OrdenesCompraModel.id_orden == request.idOrden
            ).update({"total": str(total_orden)})

            # Registrar auditoría de la actualización
            cambios_detalle = f"{productos_eliminados} eliminados, {productos_actualizados} actualizados, {productos_creados} creados"
            self.auditoria_service.registrar_actualizacion_orden(
                id_orden=request.idOrden,
                numero_oc=numero_oc,
                id_cotizacion=id_cotizacion,
                id_cotizacion_versiones=id_cotizacion_versiones,
                monto_anterior=monto_anterior,
                monto_nuevo=monto_nuevo,
                cambios_detalle=cambios_detalle,
                compra_id=None,  # No tenemos registro de compra en este contexto
                id_usuario=id_usuario
            )
            logger.info(f"Auditoría registrada para orden {numero_oc}")

            # 5. Regenerar Excel usando los datos del request
            logger.info("Regenerando archivo Excel con datos actualizados...")

            # Preparar datos de la orden (usar fecha actual para el Excel)
            fecha_actual = datetime.now().date()
            orden_data = {
                'moneda': request.moneda if request.moneda else '',
                'pago': request.pago if request.pago else '',
                'entrega': request.entrega if request.entrega else '',
                'fecha': str(fecha_actual)
            }

            # Preparar datos del proveedor (viene del request)
            proveedor_data = {
                'razonSocial': request.proveedor.razonSocial,
                'direccion': request.proveedor.direccion,
                'nombreContacto': request.proveedor.nombreContacto,
                'telefono': request.proveedor.telefono,
                'celular': request.proveedor.celular,
                'correo': request.proveedor.correo
            }

            # Preparar datos de productos (solo los NO eliminados, con datos completos del request)
            productos_data = [
                {
                    'cantidad': p.cantidad,
                    'unidadMedida': p.unidadMedida,
                    'producto': p.producto,
                    'marca': p.marca,
                    'modelo': p.modelo or '',
                    'precioUnitario': p.pUnitario,
                    'igv': p.igv
                }
                for p in request.productos if not p.eliminar
            ]

            # Generar Excel con datos actualizados
            excel_files = self.excel_generator.generate_from_data(
                orden_data=orden_data,
                productos_data=productos_data,
                proveedor_data=proveedor_data,
                numero_oc=numero_oc,
                consorcio=consorcio
            )

            if not excel_files:
                raise HTTPException(
                    status_code=500,
                    detail="No se pudo generar el archivo Excel"
                )

            # 6. Eliminar archivo antiguo de S3
            if ruta_s3_antigua:
                try:
                    logger.info(f"Eliminando archivo antiguo de S3: {ruta_s3_antigua}")
                    self.s3_service.delete_file_from_url(ruta_s3_antigua, self.bucket)
                    logger.info("Archivo antiguo eliminado de S3")
                except Exception as e:
                    logger.warning(f"No se pudo eliminar el archivo antiguo de S3: {e}")
                    # No lanzamos error aquí, continuamos con la subida del nuevo

            # 7. Subir nuevo Excel a S3
            logger.info("Subiendo nuevo archivo a S3...")
            urls = await self.file_storage.save_multiple(excel_files)

            if not urls:
                # Si falla la subida, hacer rollback de TODO
                self.db.rollback()
                raise HTTPException(
                    status_code=500,
                    detail="No se pudo subir el archivo a S3"
                )

            nueva_url_s3 = urls[0]
            logger.info(f"Nuevo archivo subido a S3: {nueva_url_s3}")

            # 8. Actualizar ruta S3 en la BD (SIN COMMIT)
            self.ordenes_compra_repo.actualizar_ruta_s3(request.idOrden, nueva_url_s3)
            logger.info("Ruta S3 actualizada en la base de datos")

            # ===================================================================
            # ✅ COMMIT ÚNICO - Si llegamos aquí, TODO está correcto
            # ===================================================================
            self.db.commit()
            logger.info("✅ COMMIT EXITOSO - Todos los cambios guardados en la BD")

            # 9. Disparar evento DESPUÉS del commit (fuera de la transacción)
            from app.adapters.outbound.database.repositories.ordenes_compra_repository import _handle_orden_compra_evento

            self.event_dispatcher.publish(
                session=self.db,
                event_data={
                    'tipo_evento': 'ORDEN_COMPRA_EDITADA',
                    'id_cotizacion_nueva': orden.id_cotizacion,
                    'id_cotizacion_versiones': orden.id_cotizacion_versiones,
                    'cambio_cotizacion': False
                },
                handler=_handle_orden_compra_evento
            )
            logger.info("✅ Evento disparado para recalcular registro de compra")

            return {
                "status": "success",
                "message": f"Orden de compra {request.idOrden} actualizada correctamente",
                "nueva_url_excel": nueva_url_s3,
                "productos_eliminados": productos_eliminados,
                "productos_actualizados": productos_actualizados,
                "productos_creados": productos_creados,
                "total_orden": float(total_orden)
            }

        except ValueError as e:
            # Rollback en caso de error de validación
            self.db.rollback()
            logger.error(f"❌ Error de validación - Rollback ejecutado: {e}")
            raise HTTPException(status_code=404, detail=str(e))

        except HTTPException as http_ex:
            # Rollback en caso de HTTPException
            self.db.rollback()
            logger.error(f"❌ HTTPException - Rollback ejecutado: {http_ex.detail}")
            raise

        except Exception as e:
            # Rollback en caso de cualquier otro error
            self.db.rollback()
            logger.error(f"❌ Error crítico - Rollback ejecutado al actualizar orden {request.idOrden}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error interno al actualizar la orden de compra: {str(e)}"
            )
