"""
Puerto para el repositorio de productos de cotizaciones.

Define el contrato para operaciones de productos de cotización.
"""
from abc import ABC, abstractmethod
from typing import List

from app.core.domain.dtos.producto_cotizacion_dtos import ProductoCotizacionDisponible


class ProductosCotizacionesRepositoryPort(ABC):
    """
    Puerto para el repositorio de productos de cotizaciones.

    Responsabilidad: Consulta de productos disponibles en cotizaciones.
    """

    @abstractmethod
    def obtener_productos_cotizaciones(
        self,
        id_cotizacion: int,
        id_cotizacion_version: int
    ) -> List[ProductoCotizacionDisponible]:
        """
        Obtiene los productos de una cotización que NO tienen OC activa asociada.

        Solo retorna productos disponibles para generar orden de compra.

        Args:
            id_cotizacion: ID de la cotización
            id_cotizacion_version: ID de la versión de la cotización

        Returns:
            List[ProductoCotizacionDisponible]: Lista de productos disponibles

        Raises:
            Exception: Si hay error en la consulta
        """
        pass