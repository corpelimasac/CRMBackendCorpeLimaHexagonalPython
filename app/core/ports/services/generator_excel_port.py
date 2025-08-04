from abc import ABC, abstractmethod
from app.adapters.inbound.api.schemas.generar_oc_schemas import GenerarOCRequest
from typing import Dict

class ExcelGeneratorPort(ABC):
    @abstractmethod
    def generate_for_order(self, request: GenerarOCRequest) -> Dict[str, bytes]:
        """Genera archivos Excel para una orden y devuelve un diccionario con nombre y contenido en bytes."""
        pass