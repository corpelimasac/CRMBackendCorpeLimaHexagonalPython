from app.core.ports.repositories.registro_compra_repository import RegistroCompraRepositoryPort
from app.adapters.outbound.database.models.registro_compra_model import RegistroCompraModel
from app.adapters.outbound.database.models.registro_compra_orden_model import RegistroCompraOrdenModel
from app.adapters.outbound.database.models.ordenes_compra_model import OrdenesCompraModel
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class RegistroCompraRepository(RegistroCompraRepositoryPort):
    """
    Implementación del repositorio de registro de compras
    """

    def __init__(self, db: Session):
        self.db = db

    def obtener_por_cotizacion(self, id_cotizacion: int) -> Optional[RegistroCompraModel]:
        """
        Obtiene el registro de compra asociado a una cotización

        Args:
            id_cotizacion: ID de la cotización

        Returns:
            RegistroCompraModel: Registro encontrado o None
        """
        try:
            registro = self.db.query(RegistroCompraModel).filter(
                RegistroCompraModel.id_cotizacion == id_cotizacion
            ).first()

            if registro:
                logger.info(f"Registro de compra encontrado para cotización {id_cotizacion}")
            else:
                logger.info(f"No existe registro de compra para cotización {id_cotizacion}")

            return registro

        except Exception as e:
            logger.error(f"Error al obtener registro de compra: {e}")
            raise

    def obtener_ordenes_por_cotizacion(self, id_cotizacion: int) -> List[OrdenesCompraModel]:
        """
        Obtiene todas las órdenes de compra de una cotización

        Args:
            id_cotizacion: ID de la cotización

        Returns:
            List[OrdenesCompraModel]: Lista de órdenes de compra
        """
        try:
            ordenes = self.db.query(OrdenesCompraModel).filter(
                OrdenesCompraModel.id_cotizacion == id_cotizacion,
                OrdenesCompraModel.activo == True
            ).all()

            logger.info(f"Encontradas {len(ordenes)} órdenes para cotización {id_cotizacion}")
            return ordenes

        except Exception as e:
            logger.error(f"Error al obtener órdenes de compra: {e}")
            raise

    def guardar_o_actualizar(
        self,
        id_cotizacion: int,
        ordenes: List[OrdenesCompraModel],
        datos_calculados: dict
    ) -> RegistroCompraModel:
        """
        Guarda o actualiza un registro de compra con sus órdenes

        Args:
            id_cotizacion: ID de la cotización
            ordenes: Lista de órdenes de compra
            datos_calculados: Diccionario con montos calculados

        Returns:
            RegistroCompraModel: Registro guardado/actualizado
        """
        try:
            # Buscar registro existente
            registro = self.obtener_por_cotizacion(id_cotizacion)

            if registro:
                logger.info(f"Actualizando registro de compra existente para cotización {id_cotizacion}")

                # Actualizar montos
                registro.monto_total_dolar = datos_calculados['monto_total_dolar']
                registro.tipo_cambio_sunat = datos_calculados['tipo_cambio_sunat']
                registro.monto_total_soles = datos_calculados['monto_total_soles']
                registro.monto_sin_igv = datos_calculados['monto_sin_igv']
                registro.fecha_orden_compra = datos_calculados['fecha_orden_compra']
                registro.tipo_empresa = datos_calculados['tipo_empresa']

                # Eliminar órdenes anteriores
                self.db.query(RegistroCompraOrdenModel).filter(
                    RegistroCompraOrdenModel.compra_id == registro.compra_id
                ).delete()

            else:
                logger.info(f"Creando nuevo registro de compra para cotización {id_cotizacion}")

                # Crear nuevo registro
                registro = RegistroCompraModel(
                    id_cotizacion=id_cotizacion,
                    fecha_orden_compra=datos_calculados['fecha_orden_compra'],
                    monto_total_dolar=datos_calculados['monto_total_dolar'],
                    tipo_cambio_sunat=datos_calculados['tipo_cambio_sunat'],
                    monto_total_soles=datos_calculados['monto_total_soles'],
                    monto_sin_igv=datos_calculados['monto_sin_igv'],
                    tipo_empresa=datos_calculados['tipo_empresa']
                )
                self.db.add(registro)
                self.db.flush()  # Obtener ID

            # Insertar órdenes actualizadas
            for orden in ordenes:
                orden_detalle = RegistroCompraOrdenModel(
                    compra_id=registro.compra_id,
                    id_orden_compra=orden.id_orden,
                    fecha_orden_compra=orden.fecha_creacion,
                    moneda=orden.moneda,
                    monto_total=orden.total
                )
                self.db.add(orden_detalle)

            self.db.commit()
            logger.info(f"✅ Registro de compra guardado exitosamente: ID {registro.compra_id}")

            return registro

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al guardar/actualizar registro de compra: {e}")
            raise

    def eliminar_orden_de_registro(self, compra_id: int, id_orden: int):
        """
        Elimina una orden específica de un registro de compra

        Args:
            compra_id: ID del registro de compra
            id_orden: ID de la orden a eliminar
        """
        try:
            self.db.query(RegistroCompraOrdenModel).filter(
                RegistroCompraOrdenModel.compra_id == compra_id,
                RegistroCompraOrdenModel.id_orden_compra == id_orden
            ).delete()

            self.db.commit()
            logger.info(f"Orden {id_orden} eliminada del registro {compra_id}")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al eliminar orden de registro: {e}")
            raise

    def eliminar_registro(self, compra_id: int):
        """
        Elimina un registro de compra completo

        Args:
            compra_id: ID del registro de compra
        """
        try:
            # Primero eliminar órdenes (por si no hay CASCADE)
            self.db.query(RegistroCompraOrdenModel).filter(
                RegistroCompraOrdenModel.compra_id == compra_id
            ).delete()

            # Luego eliminar registro
            self.db.query(RegistroCompraModel).filter(
                RegistroCompraModel.compra_id == compra_id
            ).delete()

            self.db.commit()
            logger.info(f"Registro de compra {compra_id} eliminado completamente")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al eliminar registro de compra: {e}")
            raise
