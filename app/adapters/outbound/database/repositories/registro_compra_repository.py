import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.adapters.outbound.database.models.ordenes_compra_model import OrdenesCompraModel
from app.adapters.outbound.database.models.registro_compra_model import RegistroCompraModel
from app.adapters.outbound.database.models.registro_compra_orden_model import RegistroCompraOrdenModel
from app.core.ports.repositories.registro_compra_repository import RegistroCompraRepositoryPort

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

    def obtener_registro_huerfano_por_cotizacion(self, id_cotizacion: int, id_cotizacion_versiones: int = None) -> type[
                                                                                                                       RegistroCompraModel] | None:
        """
        Busca un registro de compra huérfano (sin órdenes activas) para una cotización.

        Esto ocurre cuando se eliminan TODAS las órdenes activas pero el registro_compra
        aún existe. Busca en la tabla de auditoría para encontrar el compra_id asociado
        a esta cotización.

        Args:
            id_cotizacion: ID de la cotización
            id_cotizacion_versiones: ID de la versión de la cotización (opcional)

        Returns:
            RegistroCompraModel: Registro huérfano encontrado o None
        """
        try:
            # FIX: El compra_id se debe buscar en la tabla `registro_compra_ordenes` que es la que tiene la relación
            # con las órdenes de compra y, por lo tanto, con la cotización.
            query = self.db.query(RegistroCompraOrdenModel.compra_id).join(
                OrdenesCompraModel,
                RegistroCompraOrdenModel.id_orden == OrdenesCompraModel.id_orden
            ).filter(
                OrdenesCompraModel.id_cotizacion == id_cotizacion
            )

            if id_cotizacion_versiones is not None:
                query = query.filter(
                    OrdenesCompraModel.id_cotizacion_versiones == id_cotizacion_versiones
                )

            # Obtener el compra_id
            resultado = query.first()

            if not resultado:
                logger.info(f"No se encontró registro de compra para cotización {id_cotizacion}")
                return None

            compra_id = resultado[0]

            # Verificar si ese registro aún existe
            registro = self.db.query(RegistroCompraModel).filter(
                RegistroCompraModel.compra_id == compra_id
            ).first()

            if registro:
                # Verificar que realmente esté huérfano (sin órdenes en registro_compra_ordenes)
                ordenes_count = self.db.query(RegistroCompraOrdenModel).filter(
                    RegistroCompraOrdenModel.compra_id == compra_id
                ).count()

                if ordenes_count == 0:
                    logger.info(f"✅ Registro huérfano encontrado: compra_id={compra_id} (sin órdenes asociadas)")
                    return registro
                else:
                    logger.info(f"Registro {compra_id} encontrado pero NO está huérfano (tiene {ordenes_count} órdenes)")
                    return None
            else:
                logger.info(f"Registro de compra {compra_id} ya fue eliminado")
                return None

        except Exception as e:
            logger.error(f"Error al buscar registro huérfano: {e}", exc_info=True)
            raise

    def obtener_ordenes_por_cotizacion(self, id_cotizacion: int, id_cotizacion_versiones: int = None) -> list[
        type[OrdenesCompraModel]]:
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
                OrdenesCompraModel.activo.is_(True)
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
            id_cotizacion_versiones: ID de la versión de la cotización (opcional para compatibilidad)


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

                # Guardar datos anteriores para auditoría y detección de cambios
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
                registro.tipo_empresa = datos_calculados['tipo_empresa']
                # Actualizar fecha de actualización
                registro.fecha_actualizacion = datetime.now()

                # Detectar cambios comparando valores anteriores con nuevos
                hay_cambios = self._detectar_cambios_compra(datos_anteriores, datos_calculados)
                if hay_cambios:
                    registro.cambio_compra = True
                    logger.info("✅ Se detectaron cambios en el registro de compra - cambio_compra=True")
                else:
                    logger.info("No se detectaron cambios en el registro de compra")

                # Eliminar detalles anteriores de registro_compra_ordenes
                self.db.query(RegistroCompraOrdenModel).filter(
                    RegistroCompraOrdenModel.compra_id == registro.compra_id
                ).delete()

            else:
                logger.info(f"Creando nuevo registro de compra para cotización {id_cotizacion}")

                # Crear nuevo registro
                registro = RegistroCompraModel(
                    moneda=datos_calculados['moneda'],
                    monto_total_dolar=datos_calculados['monto_total_dolar'],
                    tipo_cambio_sunat=datos_calculados['tipo_cambio_sunat'],
                    monto_total_soles=datos_calculados['monto_total_soles'],
                    monto_sin_igv=datos_calculados['monto_sin_igv'],
                    tipo_empresa=datos_calculados['tipo_empresa'],
                    activo=True,
                    desactivado_manualmente=False,
                    fecha_creacion=datetime.now()
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

            # --- FIX: Mover la lógica de auditoría ANTES del commit ---
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

            # Commit atómico de todas las operaciones (registro, detalles, auditoría)
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

    def desactivar_registro(self, compra_id: int):
        """
        Desactiva un registro de compra cuando no quedan órdenes asociadas.
        Marca el campo 'activo' como False en lugar de eliminar el registro.
        Registra auditoría con todos los datos del registro.

        Args:
            compra_id: ID del registro de compra
        """
        from app.core.services.registro_compra_auditoria_service import RegistroCompraAuditoriaService

        try:
            # Obtener datos del registro
            registro = self.db.query(RegistroCompraModel).filter(
                RegistroCompraModel.compra_id == compra_id
            ).first()

            if not registro:
                logger.warning(f"Registro de compra {compra_id} no encontrado")
                return

            # Obtener órdenes asociadas a través de registro_compra_ordenes
            ordenes_detalle = self.db.query(RegistroCompraOrdenModel).filter(
                RegistroCompraOrdenModel.compra_id == compra_id
            ).all()

            # Si hay órdenes asociadas, obtenerlas para la auditoría
            ordenes = []
            id_cotizacion = None
            id_cotizacion_versiones = None

            if ordenes_detalle:
                ordenes_ids = [o.id_orden for o in ordenes_detalle]
                if ordenes_ids:
                    ordenes = self.db.query(OrdenesCompraModel).filter(
                        OrdenesCompraModel.id_orden.in_(ordenes_ids)
                    ).all()

                # Obtener cotización desde la primera orden
                if ordenes:
                    id_cotizacion = ordenes[0].id_cotizacion
                    id_cotizacion_versiones = ordenes[0].id_cotizacion_versiones

            # Guardar datos completos para auditoría
            datos_anteriores = {
                'compra_id': compra_id,
                'moneda': registro.moneda,
                'monto_total_dolar': float(registro.monto_total_dolar) if registro.monto_total_dolar else 0,
                'tipo_cambio_sunat': float(registro.tipo_cambio_sunat) if registro.tipo_cambio_sunat else 0,
                'monto_total_soles': float(registro.monto_total_soles) if registro.monto_total_soles else 0,
                'monto_sin_igv': float(registro.monto_sin_igv) if registro.monto_sin_igv else 0,
                'tipo_empresa': registro.tipo_empresa,
                'cantidad_ordenes': len(ordenes),
                'ordenes': [
                    {
                        'id_orden': o.id_orden,
                        'numero_oc': o.correlative,
                        'monto': float(o.total) if o.total else 0,
                        'moneda': o.moneda
                    }
                    for o in ordenes
                ]
            }

            # 1. Registrar auditoría ANTES de desactivar (dentro de la misma transacción)
            auditoria_service = RegistroCompraAuditoriaService(self.db)
            auditoria_service.registrar_desactivacion_registro(
                compra_id=compra_id,
                id_cotizacion=int(id_cotizacion) if id_cotizacion else None,
                id_cotizacion_versiones=int(id_cotizacion_versiones) if id_cotizacion_versiones else None,
                datos_anteriores=datos_anteriores,
                ordenes=ordenes,
                razon="No quedan órdenes de compra asociadas - Desactivación automática al eliminar última orden"
            )

            # 2. Marcar el registro como inactivo
            registro.activo = False
            registro.fecha_actualizacion = datetime.now()

            # 3. Commit de toda la transacción (desactivación + auditoría)
            # NOTA: NO se eliminan los detalles de registro_compra_ordenes para mantener el historial
            self.db.commit()
            logger.info(f"✅ Registro de compra {compra_id} marcado como inactivo y auditoría registrada")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al desactivar registro de compra {compra_id}: {e}", exc_info=True)
            raise

    def eliminar_registro(self, compra_id: int):
        """
        Elimina un registro de compra completo cuando no quedan órdenes asociadas.
        Registra auditoría con todos los datos del registro y órdenes antes de eliminar.

        NOTA: Este método ya NO se usa en el flujo normal de eliminación de órdenes.
        Se mantiene solo para casos especiales donde se requiera eliminación física.

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

            # Obtener órdenes asociadas a través de registro_compra_ordenes
            ordenes_detalle = self.db.query(RegistroCompraOrdenModel).filter(
                RegistroCompraOrdenModel.compra_id == compra_id
            ).all()

            # Si hay órdenes asociadas, obtenerlas para la auditoría
            ordenes = []
            id_cotizacion = None
            id_cotizacion_versiones = None

            if ordenes_detalle:
                ordenes_ids = [o.id_orden for o in ordenes_detalle]
                if ordenes_ids:
                    ordenes = self.db.query(OrdenesCompraModel).filter(
                        OrdenesCompraModel.id_orden.in_(ordenes_ids)
                    ).all()

                # Obtener cotización desde la primera orden
                if ordenes:
                    id_cotizacion = ordenes[0].id_cotizacion
                    id_cotizacion_versiones = ordenes[0].id_cotizacion_versiones

            # Guardar datos completos para auditoría
            datos_anteriores = {
                'compra_id': compra_id,
                'moneda': registro.moneda,
                'monto_total_dolar': float(registro.monto_total_dolar) if registro.monto_total_dolar else 0,
                'tipo_cambio_sunat': float(registro.tipo_cambio_sunat) if registro.tipo_cambio_sunat else 0,
                'monto_total_soles': float(registro.monto_total_soles) if registro.monto_total_soles else 0,
                'monto_sin_igv': float(registro.monto_sin_igv) if registro.monto_sin_igv else 0,
                'tipo_empresa': registro.tipo_empresa,
                'cantidad_ordenes': len(ordenes),
                'ordenes': [
                    {
                        'id_orden': o.id_orden,
                        'numero_oc': o.correlative,
                        'monto': float(o.total) if o.total else 0,
                        'moneda': o.moneda
                    }
                    for o in ordenes
                ]
            }

            # 1. Registrar auditoría ANTES de eliminar (dentro de la misma transacción)
            auditoria_service = RegistroCompraAuditoriaService(self.db)
            auditoria_service.registrar_eliminacion_registro(
                compra_id=compra_id,
                id_cotizacion=int(id_cotizacion) if id_cotizacion else None,
                id_cotizacion_versiones=int(id_cotizacion_versiones) if id_cotizacion_versiones else None,
                datos_anteriores=datos_anteriores,
                ordenes=ordenes,
                razon="No quedan órdenes de compra asociadas - Eliminación automática al eliminar última orden"
            )

            # 2. Eliminar detalles de registro_compra_ordenes
            deleted_detalles = self.db.query(RegistroCompraOrdenModel).filter(
                RegistroCompraOrdenModel.compra_id == compra_id
            ).delete()
            logger.info(f"Eliminados {deleted_detalles} detalles de registro_compra_ordenes")

            # 3. Eliminar registro principal
            self.db.query(RegistroCompraModel).filter(
                RegistroCompraModel.compra_id == compra_id
            ).delete()

            # 4. Commit de toda la transacción (eliminación + auditoría)
            self.db.commit()
            logger.info(f"✅ Registro de compra {compra_id} eliminado completamente y auditoría registrada")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al eliminar registro de compra {compra_id}: {e}", exc_info=True)
            raise

    def _detectar_cambios_compra(self, datos_anteriores: dict, datos_nuevos: dict) -> bool:
        """
        Detecta si hubo cambios en los campos relevantes del registro de compra

        Args:
            datos_anteriores: Diccionario con datos anteriores
            datos_nuevos: Diccionario con datos nuevos

        Returns:
            bool: True si hubo cambios, False si no
        """
        cambio_moneda = datos_anteriores.get('moneda') != datos_nuevos.get('moneda')
        cambio_monto_dolar = datos_anteriores.get('monto_total_dolar') != datos_nuevos.get('monto_total_dolar')
        cambio_monto_soles = datos_anteriores.get('monto_total_soles') != datos_nuevos.get('monto_total_soles')
        cambio_monto_sin_igv = datos_anteriores.get('monto_sin_igv') != datos_nuevos.get('monto_sin_igv')

        if cambio_moneda:
            logger.info(f"Cambio detectado - Moneda: {datos_anteriores.get('moneda')} → {datos_nuevos.get('moneda')}")
        if cambio_monto_dolar:
            logger.info(f"Cambio detectado - Monto Dólar: {datos_anteriores.get('monto_total_dolar')} → {datos_nuevos.get('monto_total_dolar')}")
        if cambio_monto_soles:
            logger.info(f"Cambio detectado - Monto Soles: {datos_anteriores.get('monto_total_soles')} → {datos_nuevos.get('monto_total_soles')}")
        if cambio_monto_sin_igv:
            logger.info(f"Cambio detectado - Monto Sin IGV: {datos_anteriores.get('monto_sin_igv')} → {datos_nuevos.get('monto_sin_igv')}")

        return cambio_moneda or cambio_monto_dolar or cambio_monto_soles or cambio_monto_sin_igv
