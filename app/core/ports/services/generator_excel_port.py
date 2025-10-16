from abc import ABC, abstractmethod
from app.adapters.inbound.api.schemas.generar_oc_schemas import GenerarOCRequest
from typing import Dict, List, Any

class ExcelGeneratorPort(ABC):
    @abstractmethod
    def generate_for_order(self, request: GenerarOCRequest) -> Dict[str, bytes]:
        """Genera archivos Excel para una orden y devuelve un diccionario con nombre y contenido en bytes."""
        pass

    @abstractmethod
    def generate_from_data(self, orden_data: Any, productos_data: List[Any], proveedor_data: Any, numero_oc: str, consorcio: bool = False) -> Dict[str, bytes]:
        """Genera archivos Excel a partir de datos directos sin consultar BD."""
        pass