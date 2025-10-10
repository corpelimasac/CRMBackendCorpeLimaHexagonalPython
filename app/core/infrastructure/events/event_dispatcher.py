"""
Sistema de eventos transaccionales para procesar acciones después del commit
Equivalente a @TransactionalEventListener(phase = AFTER_COMMIT) de Spring Boot
"""
from sqlalchemy import event
from sqlalchemy.orm import Session
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


def _execute_handler(event_data: dict, handler: Callable):
    """
    Ejecuta el handler en un thread separado

    El handler debe crear su propia sesión DB para tener una transacción independiente
    Equivalente a @Transactional(propagation = REQUIRES_NEW)

    Args:
        event_data: Datos del evento
        handler: Función handler a ejecutar
    """
    try:
        logger.info(f"🔄 Ejecutando handler asíncrono: {event_data.get('tipo_evento', 'UNKNOWN')}")

        # El handler es responsable de crear su propia sesión DB
        handler(event_data)

        logger.info(f"✅ Handler completado exitosamente: {event_data.get('tipo_evento', 'UNKNOWN')}")

    except Exception as e:
        logger.error(
            f"❌ Error en handler asíncrono: {e} | Evento: {event_data}",
            exc_info=True
        )
        # No propagar error - no debe afectar la transacción original (ya commiteada)


class EventDispatcher:
    """
    Despachador de eventos que se ejecutan DESPUÉS del commit exitoso

    Características:
    - AFTER_COMMIT: Solo dispara eventos si commit es exitoso
    - ASYNC: Procesamiento asíncrono usando ThreadPool
    - REQUIRES_NEW: Handlers se ejecutan con nueva sesión DB
    - Alta concurrencia: Soporta múltiples transacciones simultáneas
    """

    def __init__(self, max_workers: int = 20):
        """
        Inicializa el despachador de eventos

        Args:
            max_workers: Número máximo de workers en el ThreadPool
        """
        # ThreadPool para procesamiento asíncrono
        # Equivalente a @Async("calculoFinancieroExecutor")
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="evento-financiero-"
        )

        # Eventos pendientes por sesión
        self._pending_events: Dict[int, List[Tuple[dict, Callable]]] = {}

        logger.info(f"EventDispatcher inicializado con {max_workers} workers")

    def register_session(self, session: Session):
        """
        Registra una sesión para escuchar eventos after_commit y after_rollback

        Args:
            session: Sesión SQLAlchemy a monitorear
        """
        session_id = id(session)

        # Inicializar lista de eventos pendientes para esta sesión
        if session_id not in self._pending_events:
            self._pending_events[session_id] = []

        # Listener AFTER_COMMIT - Se ejecuta solo si commit es exitoso
        @event.listens_for(session, "after_commit", once=True)
        def receive_after_commit(session):
            logger.info(f"✅ COMMIT exitoso en sesión {session_id} - Disparando eventos")
            self._dispatch_pending_events(session_id)

        # Listener AFTER_ROLLBACK - Limpia eventos si hay rollback
        @event.listens_for(session, "after_rollback", once=True)
        def receive_after_rollback(session):
            logger.warning(f"❌ ROLLBACK en sesión {session_id} - Cancelando eventos")
            self._clear_pending_events(session_id)

    def publish(self, session: Session, event_data: dict, handler: Callable):
        """
        Publica un evento para ejecutarse DESPUÉS del commit

        El evento NO se ejecuta inmediatamente, sino que se encola y se ejecuta
        solo si el commit de la transacción es exitoso.

        Args:
            session: Sesión SQLAlchemy actual
            event_data: Datos del evento (debe ser JSON serializable)
            handler: Función handler a ejecutar (debe aceptar event_data como parámetro)
        """
        session_id = id(session)

        # Registrar sesión si aún no está registrada
        if session_id not in self._pending_events:
            self.register_session(session)

        logger.info(f"📝 Evento encolado (pendiente commit): {event_data.get('tipo_evento', 'UNKNOWN')}")
        self._pending_events[session_id].append((event_data, handler))

    def _dispatch_pending_events(self, session_id: int):
        """
        Despacha eventos pendientes de forma asíncrona

        Se ejecuta automáticamente después de un commit exitoso

        Args:
            session_id: ID de la sesión que hizo commit
        """
        events = self._pending_events.get(session_id, [])

        logger.info(f"🚀 Despachando {len(events)} eventos de forma asíncrona")

        for event_data, handler in events:
            # Ejecutar en thread pool (asíncrono, no bloquea)
            self.executor.submit(_execute_handler, event_data, handler)

        # Limpiar eventos procesados
        self._clear_pending_events(session_id)

    def _clear_pending_events(self, session_id: int):
        """
        Limpia eventos pendientes de una sesión

        Args:
            session_id: ID de la sesión
        """
        if session_id in self._pending_events:
            del self._pending_events[session_id]

    def shutdown(self, wait: bool = True):
        """
        Apaga el thread pool esperando a que terminen las tareas pendientes

        Args:
            wait: Si True, espera a que terminen todas las tareas ,
             Tiempo máximo de espera en segundos (no usado en Python < 3.9)
        """
        logger.info(f"🛑 Apagando EventDispatcher (wait={wait})")
        # ThreadPoolExecutor.shutdown() no acepta timeout hasta Python 3.9+
        # Solo usar wait=True/False
        self.executor.shutdown(wait=wait)
        logger.info("✅ EventDispatcher apagado")


# Singleton global
_event_dispatcher: EventDispatcher = None


def get_event_dispatcher() -> EventDispatcher:
    """
    Obtiene la instancia singleton del EventDispatcher

    Returns:
        EventDispatcher: Instancia global del despachador de eventos
    """
    global _event_dispatcher
    if _event_dispatcher is None:
        # Obtener configuración
        from app.config.settings import get_settings
        settings = get_settings()

        # Crear dispatcher con configuración del entorno
        _event_dispatcher = EventDispatcher(
            max_workers=settings.evento_financiero_max_workers
        )
        logger.info(
            f"EventDispatcher creado: entorno={settings.environment}, "
            f"max_workers={settings.evento_financiero_max_workers}"
        )
    return _event_dispatcher
