from abc import ABC, abstractmethod
from typing import List, Any


class ProductosCotizacionesRepositoryPort(ABC):
    """Puerto para el repositorio de productos de cotizaciones"""
    
    @abstractmethod
    def obtener_productos_cotizaciones(self, id_cotizacion: int, id_cotizacion_version: int) -> List[Any]:
        """Obtiene los datos de los productos de una cotización finalizada desde la persistencia."""
        pass