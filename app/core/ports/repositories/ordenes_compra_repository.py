from abc import ABC, abstractmethod
from app.core.domain.entities.ordenes_compra import OrdenesCompra
from app.adapters.inbound.api.schemas.generar_oc_schemas import GenerarOCRequest
from typing import List, Any, Optional

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
  def obtener_orden_por_id(self, id_orden: int, with_registro: bool = False) -> Any:
    """Obtiene una orden de compra por su ID."""
    pass

  @abstractmethod
  def eliminar_orden(self, id_orden: int) -> bool:
    """Elimina una orden de compra por su ID."""
    pass

  @abstractmethod
  def actualizar_orden(self, id_orden: int, moneda: str = None, pago: str = None, entrega: str = None, id_proveedor: int = None, id_proveedor_contacto: int = None, auto_commit: bool = True) -> bool:
    """Actualiza los campos básicos de una orden de compra."""
    pass

  @abstractmethod
  def obtener_detalles_orden(self, id_orden: int) -> List[Any]:
    """Obtiene los detalles de una orden de compra."""
    pass

  @abstractmethod
  def actualizar_detalle_producto(self, id_oc_detalle: int, cantidad: int, precio_unitario: float, precio_total: float, auto_commit: bool = True) -> bool:
    """Actualiza un detalle de producto existente."""
    pass

  @abstractmethod
  def crear_detalle_producto(self, id_orden: int, id_producto: int, cantidad: int, precio_unitario: float, precio_total: float, igv: str = 'CON IGV', id_producto_cotizacion: int = None, auto_commit: bool = True) -> Any:
    """Crea un nuevo detalle de producto."""
    pass

  @abstractmethod
  def eliminar_detalle_producto(self, id_oc_detalle: int, auto_commit: bool = True) -> bool:
    """Elimina un detalle de producto."""
    pass

  @abstractmethod
  def obtener_orden_completa(self, id_orden: int) -> Any:
    """Obtiene la orden completa con todos sus datos (proveedor, contacto, productos)."""
    pass

  @abstractmethod
  def rollback(self) -> None:
      """Hace rollback de todas las operaciones pendientes."""
      pass

  @abstractmethod
  def commit_con_evento(self, orders: List[OrdenesCompra]) -> None:
      """Hace commit de todas las operaciones pendientes y encola el evento."""
      pass

  @abstractmethod
  def actualizar_ruta_s3_sin_commit(self, id_orden: int, ruta_s3: str) -> bool:
      """Actualiza la ruta S3 de una orden SIN HACER COMMIT."""
      pass

  @abstractmethod
  def save_batch_sin_commit(self, orders: List[OrdenesCompra]) -> List[int]:
      """Guarda múltiples órdenes de compra SIN HACER COMMIT."""
      pass
