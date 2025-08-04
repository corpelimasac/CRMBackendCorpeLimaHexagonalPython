from abc import ABC, abstractmethod
from app.core.domain.entities.ordenes_compra import OrdenesCompra
from app.adapters.inbound.api.schemas.generar_oc_schemas import GenerarOCRequest
from typing import List, Any

class OrdenesCompraRepositoryPort(ABC):
  @abstractmethod
  def save(self, order: OrdenesCompra) -> OrdenesCompra:
    """Guarda una orden de compra en la base de datos."""
    pass

  @abstractmethod
  def obtener_info_oc(self, request: GenerarOCRequest) -> List[Any]:
    """Obtiene información de productos para generar orden de compra."""
    pass
