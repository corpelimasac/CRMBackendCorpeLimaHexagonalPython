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

  @abstractmethod
  def obtener_orden_por_id(self, id_orden: int) -> OrdenesCompra:
    """Obtiene una orden de compra por su ID."""
    pass

  @abstractmethod
  def eliminar_orden(self, id_orden: int) -> bool:
    """Elimina una orden de compra por su ID."""
    pass

  @abstractmethod
  def actualizar_orden(self, id_orden: int, moneda: str = None, pago: str = None, entrega: str = None) -> bool:
    """Actualiza los campos básicos de una orden de compra."""
    pass

  @abstractmethod
  def obtener_detalles_orden(self, id_orden: int) -> List[Any]:
    """Obtiene los detalles de una orden de compra."""
    pass

  @abstractmethod
  def actualizar_detalle_producto(self, id_oc_detalle: int, cantidad: int, precio_unitario: float, precio_total: float) -> bool:
    """Actualiza un detalle de producto existente."""
    pass

  @abstractmethod
  def crear_detalle_producto(self, id_orden: int, id_producto: int, cantidad: int, precio_unitario: float, precio_total: float) -> Any:
    """Crea un nuevo detalle de producto."""
    pass

  @abstractmethod
  def eliminar_detalle_producto(self, id_oc_detalle: int) -> bool:
    """Elimina un detalle de producto."""
    pass

  @abstractmethod
  def obtener_orden_completa(self, id_orden: int) -> Any:
    """Obtiene la orden completa con todos sus datos (proveedor, contacto, productos)."""
    pass
