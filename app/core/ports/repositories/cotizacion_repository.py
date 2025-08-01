from abc import ABC, abstractmethod
from app.core.domain.entities.cotizacion import Cotizacion

class CotizacionRepositoryPort(ABC):

    @abstractmethod
    def save(self, cotizacion: Cotizacion) -> Cotizacion:
        """Guarda una cotización en la base de datos."""
        pass
    
    @abstractmethod
    def get_by_id(self, id_cotizacion: int) -> Cotizacion:
        """Obtiene una cotización por su ID."""
        pass

    @abstractmethod
    def exists_by_id(self, id_cotizacion: int) -> bool:
        """Valida si existe una cotización por su ID."""
        pass

