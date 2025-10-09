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

    def obtener_por_cotizacion(self, id_cotizacion: int, id_cotizacion_versiones: int = None) -> Optional[RegistroCompraModel]:
        """
        Obtiene el registro de compra asociado a una cotización y versión
        usando join con ordenes_compra

        Args:
            id_cotizacion: ID de la cotización
            id_cotizacion_versiones: ID de la versión de la cotización (opcional para compatibilidad)

        Returns:
            RegistroCompraModel: Registro encontrado o None
        """
        try:
            # Obtener registro via join con ordenes_compra
            query = self.db.query(RegistroCompraModel).join(
                OrdenesCompraModel,
                RegistroCompraModel.compra_id == OrdenesCompraModel.compra_id
            ).filter(
                OrdenesCompraModel.id_cotizacion == id_cotizacion
            )
            
            # Filtrar por versión si se proporciona
            if id_cotizacion_versiones is not None:
                query = query.filter(
                    OrdenesCompraModel.id_cotizacion_versiones == id_cotizacion_versiones
                )
            
            registro = query.first()

            if registro:
                version_info = f" versión {id_cotizacion_versiones}" if id_cotizacion_versiones else ""
                logger.info(f"Registro de compra encontrado para cotización {id_cotizacion}{version_info}")
            else:
                version_info = f" versión {id_cotizacion_versiones}" if id_cotizacion_versiones else ""
                logger.info(f"No existe registro de compra para cotización {id_cotizacion}{version_info}")

            return registro

        except Exception as e:
            logger.error(f"Error al obtener registro de compra: {e}")
            raise

    def obtener_ordenes_por_cotizacion(self, id_cotizacion: int, id_cotizacion_versiones: int = None) -> List[OrdenesCompraModel]:
        """
        Obtiene todas las órdenes de compra de una cotización y versión específica

        Args:
            id_cotizacion: ID de la cotización
            id_cotizacion_versiones: ID de la versión de la cotización (opcional para compatibilidad)

        Returns:
            List[OrdenesCompraModel]: Lista de órdenes de compra
        """
        try:
            query = self.db.query(OrdenesCompraModel).filter(
                OrdenesCompraModel.id_cotizacion == id_cotizacion,
                OrdenesCompraModel.activo == True
            )
            
            # Filtrar por versión si se proporciona
            if id_cotizacion_versiones is not None:
                query = query.filter(
                    OrdenesCompraModel.id_cotizacion_versiones == id_cotizacion_versiones
                )
            
            ordenes = query.all()

            version_info = f" versión {id_cotizacion_versiones}" if id_cotizacion_versiones else ""
            logger.info(f"Encontradas {len(ordenes)} órdenes para cotización {id_cotizacion}{version_info}")
            return ordenes

        except Exception as e:
            logger.error(f"Error al obtener órdenes de compra: {e}")
            raise

    def guardar_o_actualizar(
        self,
        id_cotizacion: int,
        ordenes: List[OrdenesCompraModel],
        datos_calculados: dict,
        id_cotizacion_versiones: int = None
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
            registro = self.obtener_por_cotizacion(id_cotizacion, id_cotizacion_versiones)

            if registro:
                logger.info(f"Actualizando registro de compra existente para cotización {id_cotizacion}")

                # Actualizar montos
                registro.moneda = datos_calculados['moneda']
                registro.monto_total_dolar = datos_calculados['monto_total_dolar']
                registro.tipo_cambio_sunat = datos_calculados['tipo_cambio_sunat']
                registro.monto_total_soles = datos_calculados['monto_total_soles']
                registro.monto_sin_igv = datos_calculados['monto_sin_igv']
                registro.fecha_orden_compra = datos_calculados['fecha_orden_compra']
                registro.tipo_empresa = datos_calculados['tipo_empresa']

                # Eliminar detalles anteriores de registro_compra_ordenes
                self.db.query(RegistroCompraOrdenModel).filter(
                    RegistroCompraOrdenModel.compra_id == registro.compra_id
                ).delete()

            else:
                logger.info(f"Creando nuevo registro de compra para cotización {id_cotizacion}")

                # Crear nuevo registro
                registro = RegistroCompraModel(
                    fecha_orden_compra=datos_calculados['fecha_orden_compra'],
                    moneda=datos_calculados['moneda'],
                    monto_total_dolar=datos_calculados['monto_total_dolar'],
                    tipo_cambio_sunat=datos_calculados['tipo_cambio_sunat'],
                    monto_total_soles=datos_calculados['monto_total_soles'],
                    monto_sin_igv=datos_calculados['monto_sin_igv'],
                    tipo_empresa=datos_calculados['tipo_empresa']
                )
                self.db.add(registro)
                self.db.flush()  # Obtener ID

            # Actualizar compra_id en ordenes_compra y crear detalles en registro_compra_ordenes
            for orden in ordenes:
                # Actualizar compra_id en la orden de compra
                orden.compra_id = registro.compra_id

                # Crear detalle en registro_compra_ordenes (tabla histórica)
                # Normalizar moneda a formato corto
                moneda_corta = 'USD' if orden.moneda and orden.moneda.upper() in ('USD', 'DOLARES') else 'PEN'

                orden_detalle = RegistroCompraOrdenModel(
                    compra_id=registro.compra_id,
                    fecha_orden_compra=orden.fecha_creacion,
                    moneda=moneda_corta,
                    monto_total=orden.total if orden.total else 0
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
        (actualiza compra_id a NULL en la orden y elimina de registro_compra_ordenes)

        Args:
            compra_id: ID del registro de compra
            id_orden: ID de la orden a eliminar
        """
        try:
            # Actualizar compra_id a NULL en la orden
            orden = self.db.query(OrdenesCompraModel).filter(
                OrdenesCompraModel.id_orden == id_orden,
                OrdenesCompraModel.compra_id == compra_id
            ).first()

            if orden:
                # Desvincular orden
                orden.compra_id = None

                # Eliminar detalles de registro_compra_ordenes
                # (Nota: No hay FK directa a id_orden, se eliminan todos del compra_id
                # y se recalculan en la siguiente actualización)

                self.db.commit()
                logger.info(f"Orden {id_orden} desvinculada del registro {compra_id}")
            else:
                logger.warning(f"Orden {id_orden} no encontrada en registro {compra_id}")

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
            # Primero desvincular todas las órdenes asociadas
            self.db.query(OrdenesCompraModel).filter(
                OrdenesCompraModel.compra_id == compra_id
            ).update({'compra_id': None})

            # Eliminar detalles de registro_compra_ordenes (por CASCADE o manualmente)
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
