import logging
from app.core.ports.repositories.ordenes_compra_repository import OrdenesCompraRepositoryPort
from app.adapters.outbound.external_services.aws.s3_service import S3Service
from fastapi import HTTPException
from app.config.settings import get_settings

logger = logging.getLogger(__name__)


class EliminarOrdenCompra:
    """
    Caso de uso para eliminar una orden de compra.

    Este caso de uso:
    1. Obtiene la orden de compra por su ID
    2. Elimina el archivo asociado de S3 (si existe)
    3. Elimina la orden de compra de la base de datos

    Siguiendo la arquitectura hexagonal:
    - Capa de aplicación (use case)
    - Se comunica con puertos (repositories)
    - Los adaptadores implementan los puertos
    """

    def __init__(
        self,
        ordenes_compra_repo: OrdenesCompraRepositoryPort,
        s3_service: S3Service = None
    ):
        """
        Inicializa el caso de uso con las dependencias necesarias.

        Args:
            ordenes_compra_repo: Repositorio de órdenes de compra
            s3_service: Servicio de S3 (opcional, se crea uno nuevo si no se proporciona)
        """
        self.ordenes_compra_repo = ordenes_compra_repo
        self.s3_service = s3_service or S3Service()
        # Centralizar lectura del bucket desde settings para evitar desincronización
        self.bucket = get_settings().aws_bucket_name

    def execute(self, id_orden: int) -> dict:
        """
        Ejecuta el caso de uso de eliminación de orden de compra.

        Args:
            id_orden (int): ID de la orden de compra a eliminar

        Returns:
            dict: Resultado de la operación con status y mensaje

        Raises:
            HTTPException: Si hay errores durante el proceso
        """
        try:
            logger.info(f"Iniciando eliminación de orden de compra ID: {id_orden}")

            # 1. Obtener la orden de compra
            orden = self.ordenes_compra_repo.obtener_orden_por_id(id_orden)

            if not orden:
                raise HTTPException(
                    status_code=404,
                    detail=f"Orden de compra con ID {id_orden} no encontrada"
                )

            logger.info(f"Orden encontrada: {orden.correlative if hasattr(orden, 'correlative') else id_orden}")

            # 2. Eliminar archivo de S3 si existe
            s3_deleted = False
            if hasattr(orden, 'ruta_s3') and orden.ruta_s3:
                try:
                    logger.info(f"Eliminando archivo de S3: {orden.ruta_s3}")
                    self.s3_service.delete_file_from_url(orden.ruta_s3, self.bucket)
                    s3_deleted = True
                    logger.info(f"Archivo eliminado exitosamente de S3")
                except Exception as e:
                    logger.error(f"Error al eliminar archivo de S3: {e}")
                    # IMPORTANTE: Si falla la eliminación de S3, NO continuar con la BD
                    raise HTTPException(
                        status_code=500,
                        detail=f"No se pudo eliminar el archivo de S3. La orden no fue eliminada. Error: {str(e)}"
                    )
            else:
                logger.info("La orden no tiene archivo asociado en S3")

            # 3. Eliminar la orden de compra de la base de datos
            logger.info(f"Eliminando orden de compra de la base de datos")
            self.ordenes_compra_repo.eliminar_orden(id_orden)
            logger.info(f"Orden de compra {id_orden} eliminada exitosamente de la base de datos")

            return {
                "status": "success",
                "message": f"Orden de compra {id_orden} eliminada correctamente",
                "s3_file_deleted": s3_deleted,
                "database_deleted": True
            }

        except ValueError as e:
            logger.error(f"Error de validación: {e}")
            raise HTTPException(status_code=404, detail=str(e))

        except HTTPException:
            raise

        except Exception as e:
            logger.error(f"Error al eliminar orden de compra {id_orden}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error interno al eliminar la orden de compra: {str(e)}"
            )
