"""
Puerto para operaciones de escritura de órdenes de compra.

Este puerto sigue el principio de segregación de interfaces (ISP).
"""
from abc import ABC, abstractmethod
from typing import List

from app.core.domain.entities.ordenes_compra import OrdenesCompra


class OrdenesCompraWritePort(ABC):
    """
    Puerto para operaciones de escritura de órdenes de compra.

    Responsabilidad: Persistencia y modificación de órdenes de compra.
    """

    @abstractmethod
    def save_batch_sin_commit(self, orders: List[OrdenesCompra]) -> List[int]:
        """
        Guarda múltiples órdenes de compra SIN HACER COMMIT.

        Este método hace flush para obtener los IDs generados pero no confirma
        la transacción. Útil para operaciones que requieren post-procesamiento
        antes del commit final.

        Args:
            orders: Lista de entidades OrdenesCompra a guardar

        Returns:
            List[int]: Lista de IDs de las órdenes creadas

        Raises:
            OrdenCompraError: Si hay error en la persistencia
        """
        pass

    @abstractmethod
    def actualizar_ruta_s3_sin_commit(self, id_orden: int, ruta_s3: str) -> bool:
        """
        Actualiza la ruta S3 de una orden SIN HACER COMMIT.

        Args:
            id_orden: ID de la orden a actualizar
            ruta_s3: Nueva ruta S3

        Returns:
            bool: True si se actualizó correctamente

        Raises:
            OrdenCompraNotFoundError: Si no existe la orden
        """
        pass

    @abstractmethod
    def actualizar_ruta_s3(self, id_orden: int, ruta_s3: str) -> bool:
        """
        Actualiza la ruta S3 de una orden de compra específica.

        Args:
            id_orden: ID de la orden a actualizar
            ruta_s3: Nueva ruta S3

        Returns:
            bool: True si se actualizó correctamente

        Raises:
            OrdenCompraNotFoundError: Si no existe la orden
        """
        pass

    @abstractmethod
    def actualizar_orden(
        self,
        id_orden: int,
        moneda: str = None,
        pago: str = None,
        entrega: str = None,
        id_proveedor: int = None,
        id_proveedor_contacto: int = None,
        auto_commit: bool = True
    ) -> bool:
        """
        Actualiza los campos básicos de una orden de compra.

        Args:
            id_orden: ID de la orden a actualizar
            moneda: Nueva moneda (opcional)
            pago: Nuevos términos de pago (opcional)
            entrega: Nuevos términos de entrega (opcional)
            id_proveedor: Nuevo ID de proveedor (opcional)
            id_proveedor_contacto: Nuevo ID de contacto (opcional)
            auto_commit: Si debe hacer commit automáticamente

        Returns:
            bool: True si se actualizó correctamente

        Raises:
            OrdenCompraNotFoundError: Si no existe la orden
            ActualizacionOrdenError: Si hay error en la actualización
        """
        pass

    @abstractmethod
    def actualizar_detalle_producto(
        self,
        id_oc_detalle: int,
        cantidad: int,
        precio_unitario: float,
        precio_total: float,
        auto_commit: bool = True
    ) -> bool:
        """
        Actualiza un detalle de producto existente.

        Args:
            id_oc_detalle: ID del detalle a actualizar
            cantidad: Nueva cantidad
            precio_unitario: Nuevo precio unitario
            precio_total: Nuevo precio total
            auto_commit: Si debe hacer commit automáticamente

        Returns:
            bool: True si se actualizó correctamente

        Raises:
            OrdenCompraError: Si hay error en la actualización
        """
        pass

    @abstractmethod
    def crear_detalle_producto(
        self,
        id_orden: int,
        id_producto: int,
        cantidad: int,
        precio_unitario: float,
        precio_total: float,
        igv: str = 'CON IGV',
        id_producto_cotizacion: int = None,
        auto_commit: bool = True
    ) -> int:
        """
        Crea un nuevo detalle de producto.

        Args:
            id_orden: ID de la orden
            id_producto: ID del producto
            cantidad: Cantidad
            precio_unitario: Precio unitario
            precio_total: Precio total
            igv: Tipo de IGV ('CON IGV' o 'SIN IGV')
            id_producto_cotizacion: ID del producto en cotización
            auto_commit: Si debe hacer commit automáticamente

        Returns:
            int: ID del detalle creado

        Raises:
            OrdenCompraNotFoundError: Si no existe la orden
        """
        pass

    @abstractmethod
    def eliminar_detalle_producto(self, id_oc_detalle: int, auto_commit: bool = True) -> bool:
        """
        Elimina un detalle de producto.

        Args:
            id_oc_detalle: ID del detalle a eliminar
            auto_commit: Si debe hacer commit automáticamente

        Returns:
            bool: True si se eliminó correctamente

        Raises:
            OrdenCompraError: Si hay error en la eliminación
        """
        pass

    @abstractmethod
    def eliminar_orden(self, id_orden: int) -> bool:
        """
        Elimina una orden de compra por su ID.

        Args:
            id_orden: ID de la orden a eliminar

        Returns:
            bool: True si se eliminó correctamente

        Raises:
            OrdenCompraNotFoundError: Si no existe la orden
            EliminacionOrdenError: Si hay error en la eliminación
        """
        pass
