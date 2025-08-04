from abc import ABC, abstractmethod
from app.core.domain.entities.cotizacion import Cotizacion

class CotizacionVersionesRepositoryPort(ABC):

    @abstractmethod
    def get_by_id(self, id_cotizacion_version: int) -> Cotizacion:
        """Obtiene una cotización por su ID."""
        pass

    @abstractmethod
    def exists_by_id(self, id_cotizacion_version: int) -> bool: 
        pass