"""
Puerto para generación de archivos Excel de órdenes de compra.

Define el contrato para generadores de Excel independiente de la implementación.
"""
from abc import ABC, abstractmethod
from typing import Dict, List

from app.core.domain.dtos.orden_compra_dtos import (
    ObtenerInfoOCQuery,
    DatosOrdenExcel,
    DatosProveedorExcel,
    DatosProductoExcel,
)


class ExcelGeneratorPort(ABC):
    """
    Puerto para generación de archivos Excel de órdenes de compra.

    Responsabilidad: Generar archivos Excel para órdenes de compra.
    """

    @abstractmethod
    def generate_for_order(self, query: ObtenerInfoOCQuery) -> Dict[str, bytes]:
        """
        Genera archivos Excel para una orden consultando la base de datos.

        Args:
            query: Query del dominio con los criterios para generar OC

        Returns:
            Dict[str, bytes]: Diccionario con nombre de archivo como clave
                             y contenido en bytes como valor

        Raises:
            DatosInsuficientesError: Si no hay datos para generar Excel
        """
        pass

    @abstractmethod
    def generate_from_data(
        self,
        orden_data: DatosOrdenExcel,
        productos_data: List[DatosProductoExcel],
        proveedor_data: DatosProveedorExcel,
        numero_oc: str,
        consorcio: bool = False
    ) -> Dict[str, bytes]:
        """
        Genera archivos Excel a partir de datos directos sin consultar BD.

        Args:
            orden_data: Datos de la orden
            productos_data: Lista de productos
            proveedor_data: Datos del proveedor y contacto
            numero_oc: Número de la orden de compra
            consorcio: Si es consorcio

        Returns:
            Dict[str, bytes]: Diccionario con nombre de archivo y contenido en bytes

        Raises:
            GeneracionExcelError: Si hay error al generar el Excel
        """
        pass