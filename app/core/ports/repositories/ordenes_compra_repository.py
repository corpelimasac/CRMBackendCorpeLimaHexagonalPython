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
  def save_batch(self, orders: List[OrdenesCompra]) -> List[OrdenesCompra]:
    """Guarda múltiples órdenes de compra en una sola transacción."""
    pass

  @abstractmethod
  def obtener_info_oc(self, request: GenerarOCRequest) -> List[Any]:
    """Obtiene información de productos para generar orden de compra."""
    pass

  @abstractmethod
  def actualizar_ruta_s3(self, id_orden: int, ruta_s3: str) -> bool:
    """Actualiza la ruta S3 de una orden de compra específica."""
    pass

  @abstractmethod
  def obtener_ordenes_por_contacto_y_version(self, id_cotizacion: int, id_version: int, id_contacto: int) -> List[Any]:
    """Obtiene las órdenes de compra de un contacto específico en una versión de cotización."""
    pass
