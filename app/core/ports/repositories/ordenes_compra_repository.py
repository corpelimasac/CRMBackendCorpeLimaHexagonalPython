from abc import ABC, abstractmethod
from app.core.domain.entities.ordenes_compra import PurchaseOrder

class OrdenesCompraRepositoryPort(ABC):
    @abstractmethod
    def create_purchase_order(self, purchase_order: PurchaseOrder) -> None:
        pass