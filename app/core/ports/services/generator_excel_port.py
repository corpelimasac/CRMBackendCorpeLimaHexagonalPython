from abc import ABC, abstractmethod
from app.core.domain.entities.ordenes_compra import OrdenesCompra

class ExcelGeneratorPort(ABC):
    @abstractmethod
    def generate_for_order(self, order: OrdenesCompra) -> bytes:
        """Genera un archivo Excel para una orden y devuelve su contenido en bytes."""
        pass