from abc import ABC, abstractmethod
from app.core.domain.entities.ordenes_compra import OrdenesCompra

class OrdenesCompraRepositoryPort(ABC):
  @abstractmethod
  def save(self, order: OrdenesCompra) -> OrdenesCompra:
    """Guarda una orden de compra en la base de datos."""
    pass