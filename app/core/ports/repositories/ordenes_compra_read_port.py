"""
Puerto para operaciones de lectura de órdenes de compra.

Este puerto sigue el principio de segregación de interfaces (ISP).
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.core.domain.dtos.orden_compra_dtos import (
    DetalleProductoOC,
    OrdenCompraCompleta,
)


class OrdenesCompraReadPort(ABC):
    """
    Puerto para operaciones de lectura de órdenes de compra.

    Responsabilidad: Consultas de órdenes de compra existentes.
    """

    @abstractmethod
    def obtener_orden_por_id(self, id_orden: int, with_registro: bool = False) -> Optional[OrdenCompraCompleta]:
        """
        Obtiene una orden de compra por su ID.

        Args:
            id_orden: ID de la orden a buscar
            with_registro: Si debe incluir información de registro de compra

        Returns:
            Optional[OrdenCompraCompleta]: Orden completa o None si no existe

        Raises:
            OrdenCompraNotFoundError: Si no existe la orden
        """
        pass

    @abstractmethod
    def obtener_detalles_orden(self, id_orden: int) -> List[DetalleProductoOC]:
        """
        Obtiene los detalles (productos) de una orden de compra.

        Args:
            id_orden: ID de la orden

        Returns:
            List[DetalleProductoOC]: Lista de productos de la orden

        Raises:
            OrdenCompraNotFoundError: Si no existe la orden
        """
        pass

    @abstractmethod
    def obtener_orden_completa(self, id_orden: int) -> OrdenCompraCompleta:
        """
        Obtiene la orden completa con todos sus datos (proveedor, contacto, productos).

        Args:
            id_orden: ID de la orden

        Returns:
            OrdenCompraCompleta: Datos completos de la orden

        Raises:
            OrdenCompraNotFoundError: Si no existe la orden
        """
        pass

    @abstractmethod
    def obtener_ordenes_por_contacto_y_version(
        self,
        id_cotizacion: int,
        id_version: int,
        id_contacto: int
    ) -> List[OrdenCompraCompleta]:
        """
        Obtiene las órdenes de compra de un contacto específico en una versión de cotización.

        Args:
            id_cotizacion: ID de la cotización
            id_version: ID de la versión de cotización
            id_contacto: ID del contacto del proveedor

        Returns:
            List[OrdenCompraCompleta]: Lista de órdenes del contacto
        """
        pass
