"""
Caso de uso que procesa el registro de compras después de crear/editar OC
Se ejecuta en NUEVA TRANSACCIÓN después del commit de la OC (asíncrono)
"""
from sqlalchemy.orm import Session
from app.adapters.outbound.database.repositories.registro_compra_repository import RegistroCompraRepository
from app.adapters.outbound.database.repositories.tipo_cambio_repository import TipoCambioRepository
from app.core.services.registro_compra_service import RegistroCompraService
import logging

logger = logging.getLogger(__name__)


class ProcesarRegistroCompra:
    """
    Caso de uso que procesa el registro de compra

    Se ejecuta en NUEVA TRANSACCIÓN después del commit de la OC
    Equivalente a @Transactional(propagation = REQUIRES_NEW)
    """

    def __init__(self, db: Session):
        self.db = db
        self.registro_repo = RegistroCompraRepository(db)
        self.tc_repo = TipoCambioRepository(db)
        self.service = RegistroCompraService()

    def execute(self, event_data: dict):
        """
        Procesa el evento de creación/edición de OC

        Args:
            event_data: Diccionario con datos del evento
        """
        try:
            tipo_evento = event_data.get('tipo_evento')
            logger.info(f"🔄 Procesando evento: {tipo_evento}")

            if tipo_evento == 'ORDEN_COMPRA_CREADA':
                self._handle_creacion(event_data)
            elif tipo_evento == 'ORDEN_COMPRA_EDITADA':
                self._handle_edicion(event_data)
            else:
                logger.warning(f"Tipo de evento desconocido: {tipo_evento}")

            logger.info(f"✅ Evento procesado exitosamente")

        except Exception as e:
            logger.error(f"❌ Error procesando evento: {e}", exc_info=True)
            self.db.rollback()
            raise

    def _procesar_y_guardar_registro(self, id_cotizacion: int, id_cotizacion_versiones: int):
        """
        Método común para procesar y guardar/actualizar registro de compra

        Args:
            id_cotizacion: ID de la cotización
            id_cotizacion_versiones: ID de la versión de cotización
        """
        # Obtener todas las OC ACTIVAS de esta cotización y versión
        ordenes = self.registro_repo.obtener_ordenes_por_cotizacion(id_cotizacion, id_cotizacion_versiones)

        if not ordenes:
            logger.warning(f"No se encontraron órdenes activas para cotización {id_cotizacion} versión {id_cotizacion_versiones}")

            # Buscar si existe un registro huérfano (puede tener referencias a órdenes inactivas)
            registro_existente = self.registro_repo.obtener_registro_huerfano_por_cotizacion(
                id_cotizacion, id_cotizacion_versiones
            )

            if registro_existente:
                logger.info(
                    f"📍 Registro huérfano encontrado (compra_id: {registro_existente.compra_id}) "
                    f"para cotización {id_cotizacion} versión {id_cotizacion_versiones}. "
                    f"Procediendo a eliminar registro completo..."
                )
                self.registro_repo.eliminar_registro(registro_existente.compra_id)
            else:
                logger.info(f"No existe registro de compra para eliminar (cotización {id_cotizacion})")

            return

        # Verificar si ya existe registro
        registro_existente = self.registro_repo.obtener_por_cotizacion(id_cotizacion, id_cotizacion_versiones)

        if registro_existente:
            # Recalcular con TC guardado
            tc = registro_existente.tipo_cambio_sunat
            logger.info(f"Registro existente encontrado - Usando TC guardado: {tc}")
        else:
            # Primera OC, consultar TC SUNAT
            tc = self.tc_repo.obtener_tipo_cambio_mas_reciente()
            if not tc:
                logger.error("No se pudo obtener tipo de cambio de SUNAT")
                raise ValueError("Tipo de cambio SUNAT no disponible")
            logger.info(f"Primera OC - Consultando TC SUNAT: {tc}")

        # Calcular montos
        datos = self.service.calcular_montos_consolidados(ordenes, tc)

        # Guardar o actualizar
        self.registro_repo.guardar_o_actualizar(
            id_cotizacion=id_cotizacion,
            ordenes=ordenes,
            datos_calculados=datos,
            id_cotizacion_versiones=id_cotizacion_versiones
        )

        logger.info(f"✅ Registro de compra guardado para cotización {id_cotizacion} versión {id_cotizacion_versiones}")

    def _handle_creacion(self, event_data: dict):
        """
        Maneja la creación de una nueva orden de compra

        Args:
            event_data: Datos del evento
        """
        id_cotizacion = event_data['id_cotizacion']
        id_cotizacion_versiones = event_data.get('id_cotizacion_versiones')

        logger.info(f"Procesando creación de OC para cotización {id_cotizacion} versión {id_cotizacion_versiones}")
        self._procesar_y_guardar_registro(id_cotizacion, id_cotizacion_versiones)

    def _handle_edicion(self, event_data: dict):
        """
        Maneja la edición de una orden de compra

        Args:
            event_data: Datos del evento
        """
        if event_data.get('cambio_cotizacion'):
            logger.info("Detectado cambio de cotización")
            self._handle_cambio_cotizacion(event_data)
        else:
            logger.info("Edición en misma cotización")
            self._handle_edicion_misma_cotizacion(event_data)

    def _handle_edicion_misma_cotizacion(self, event_data: dict):
        """
        Maneja edición de OC sin cambio de cotización

        Args:
            event_data: Datos del evento
        """
        id_cotizacion = event_data['id_cotizacion_nueva']
        id_cotizacion_versiones = event_data.get('id_cotizacion_versiones')

        logger.info(f"Recalculando registro para cotización {id_cotizacion} versión {id_cotizacion_versiones}")
        self._procesar_y_guardar_registro(id_cotizacion, id_cotizacion_versiones)

    def _handle_cambio_cotizacion(self, event_data: dict):
        """
        Maneja edición de OC con cambio de cotización

        Elimina OC de cotización anterior y la agrega a la nueva

        Args:
            event_data: Datos del evento
        """
        id_cotizacion_anterior = event_data['id_cotizacion_anterior']
        id_cotizacion_nueva = event_data['id_cotizacion_nueva']
        id_cotizacion_versiones_anterior = event_data.get('id_cotizacion_versiones_anterior')
        id_cotizacion_versiones_nueva = event_data.get('id_cotizacion_versiones_nueva')
        id_orden = event_data['id_orden']

        logger.info(
            f"Moviendo OC {id_orden} de cotización {id_cotizacion_anterior} versión {id_cotizacion_versiones_anterior} "
            f"a cotización {id_cotizacion_nueva} versión {id_cotizacion_versiones_nueva}"
        )

        # === PASO 1: Limpiar cotización anterior ===
        logger.info(f"Procesando cotización anterior {id_cotizacion_anterior} versión {id_cotizacion_versiones_anterior}")
        self._procesar_y_guardar_registro(id_cotizacion_anterior, id_cotizacion_versiones_anterior)

        # === PASO 2: Agregar a nueva cotización ===
        logger.info(f"Procesando nueva cotización {id_cotizacion_nueva} versión {id_cotizacion_versiones_nueva}")
        self._procesar_y_guardar_registro(id_cotizacion_nueva, id_cotizacion_versiones_nueva)

        logger.info(
            f"✅ OC movida exitosamente de cotización {id_cotizacion_anterior} "
            f"a {id_cotizacion_nueva}"
        )
