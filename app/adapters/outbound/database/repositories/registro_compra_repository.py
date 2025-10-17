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
            # Obtener registro via join con registro_compra_ordenes -> ordenes_compra
            query = self.db.query(RegistroCompraModel).join(
                RegistroCompraOrdenModel,
                RegistroCompraModel.compra_id == RegistroCompraOrdenModel.compra_id
            ).join(
                OrdenesCompraModel,
                RegistroCompraOrdenModel.id_orden == OrdenesCompraModel.id_orden
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
        from app.core.services.registro_compra_auditoria_service import RegistroCompraAuditoriaService

        try:
            # Inicializar servicio de auditoría
            auditoria_service = RegistroCompraAuditoriaService(self.db)

            # Buscar registro existente
            registro = self.obtener_por_cotizacion(id_cotizacion, id_cotizacion_versiones)

            # Guardar estado anterior para auditoría
            datos_anteriores = None
            ordenes_anteriores = []
            es_actualizacion = False

            if registro:
                es_actualizacion = True
                logger.info(f"Actualizando registro de compra existente para cotización {id_cotizacion}")

                # Guardar datos anteriores para auditoría
                datos_anteriores = {
                    'moneda': registro.moneda,
                    'monto_total_dolar': float(registro.monto_total_dolar) if registro.monto_total_dolar else 0,
                    'tipo_cambio_sunat': float(registro.tipo_cambio_sunat) if registro.tipo_cambio_sunat else 0,
                    'monto_total_soles': float(registro.monto_total_soles) if registro.monto_total_soles else 0,
                    'monto_sin_igv': float(registro.monto_sin_igv) if registro.monto_sin_igv else 0,
                    'tipo_empresa': registro.tipo_empresa
                }

                # Obtener órdenes anteriores
                ordenes_anteriores_query = self.db.query(RegistroCompraOrdenModel).filter(
                    RegistroCompraOrdenModel.compra_id == registro.compra_id
                ).all()
                ordenes_anteriores = self.db.query(OrdenesCompraModel).filter(
                    OrdenesCompraModel.id_orden.in_([o.id_orden for o in ordenes_anteriores_query])
                ).all()

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

            # Crear detalles en registro_compra_ordenes con relación a las órdenes
            for orden in ordenes:
                # Crear detalle en registro_compra_ordenes con FK a orden de compra
                # Normalizar moneda a formato corto
                moneda_corta = 'USD' if orden.moneda and orden.moneda.upper() in ('USD', 'DOLARES') else 'PEN'

                orden_detalle = RegistroCompraOrdenModel(
                    compra_id=registro.compra_id,
                    id_orden=orden.id_orden,  # FK a orden de compra (One-to-One)
                    fecha_orden_compra=orden.fecha_creacion,
                    moneda=moneda_corta,
                    monto_total=orden.total if orden.total else 0
                )
                self.db.add(orden_detalle)

            self.db.commit()
            logger.info(f"✅ Registro de compra guardado exitosamente: ID {registro.compra_id}")

            # Registrar auditoría
            if es_actualizacion:
                auditoria_service.registrar_actualizacion_registro(
                    compra_id=registro.compra_id,
                    id_cotizacion=id_cotizacion,
                    id_cotizacion_versiones=id_cotizacion_versiones,
                    datos_anteriores=datos_anteriores,
                    datos_nuevos=datos_calculados,
                    ordenes_anteriores=ordenes_anteriores,
                    ordenes_nuevas=ordenes
                )
            else:
                auditoria_service.registrar_creacion_registro(
                    compra_id=registro.compra_id,
                    id_cotizacion=id_cotizacion,
                    id_cotizacion_versiones=id_cotizacion_versiones,
                    datos_nuevos=datos_calculados,
                    ordenes=ordenes
                )

            return registro

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al guardar/actualizar registro de compra: {e}")
            raise

    def eliminar_orden_de_registro(self, compra_id: int, id_orden: int):
        """
        Elimina una orden específica de un registro de compra
        (elimina el registro en registro_compra_ordenes)

        Args:
            compra_id: ID del registro de compra
            id_orden: ID de la orden a eliminar
        """
        try:
            # Eliminar registro de registro_compra_ordenes
            orden_detalle = self.db.query(RegistroCompraOrdenModel).filter(
                RegistroCompraOrdenModel.compra_id == compra_id,
                RegistroCompraOrdenModel.id_orden == id_orden
            ).first()

            if orden_detalle:
                self.db.delete(orden_detalle)
                self.db.commit()
                logger.info(f"Orden {id_orden} eliminada del registro {compra_id}")
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
        from app.core.services.registro_compra_auditoria_service import RegistroCompraAuditoriaService

        try:
            # Obtener datos antes de eliminar para auditoría
            registro = self.db.query(RegistroCompraModel).filter(
                RegistroCompraModel.compra_id == compra_id
            ).first()

            if not registro:
                logger.warning(f"Registro de compra {compra_id} no encontrado")
                return

            # Obtener órdenes asociadas
            ordenes_detalle = self.db.query(RegistroCompraOrdenModel).filter(
                RegistroCompraOrdenModel.compra_id == compra_id
            ).all()

            ordenes = self.db.query(OrdenesCompraModel).filter(
                OrdenesCompraModel.id_orden.in_([o.id_orden for o in ordenes_detalle])
            ).all()

            # Obtener cotización desde la primera orden
            id_cotizacion = ordenes[0].id_cotizacion if ordenes else None
            id_cotizacion_versiones = ordenes[0].id_cotizacion_versiones if ordenes else None

            # Guardar datos para auditoría
            datos_anteriores = {
                'moneda': registro.moneda,
                'monto_total_dolar': float(registro.monto_total_dolar) if registro.monto_total_dolar else 0,
                'tipo_cambio_sunat': float(registro.tipo_cambio_sunat) if registro.tipo_cambio_sunat else 0,
                'monto_total_soles': float(registro.monto_total_soles) if registro.monto_total_soles else 0,
                'monto_sin_igv': float(registro.monto_sin_igv) if registro.monto_sin_igv else 0,
                'tipo_empresa': registro.tipo_empresa
            }

            # Eliminar detalles de registro_compra_ordenes
            self.db.query(RegistroCompraOrdenModel).filter(
                RegistroCompraOrdenModel.compra_id == compra_id
            ).delete()

            # Eliminar registro principal
            self.db.query(RegistroCompraModel).filter(
                RegistroCompraModel.compra_id == compra_id
            ).delete()

            self.db.commit()
            logger.info(f"Registro de compra {compra_id} eliminado completamente")

            # Registrar auditoría
            auditoria_service = RegistroCompraAuditoriaService(self.db)
            auditoria_service.registrar_eliminacion_registro(
                compra_id=compra_id,
                id_cotizacion=id_cotizacion,
                id_cotizacion_versiones=id_cotizacion_versiones,
                datos_anteriores=datos_anteriores,
                ordenes=ordenes,
                razon="No quedan órdenes de compra asociadas"
            )

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al eliminar registro de compra: {e}")
            raise
