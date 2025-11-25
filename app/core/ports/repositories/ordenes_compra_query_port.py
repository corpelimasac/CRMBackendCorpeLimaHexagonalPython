"""
Puerto para consultas especializadas de órdenes de compra.

Este puerto sigue el principio de segregación de interfaces (ISP).
"""
from abc import ABC, abstractmethod
from typing import List

from app.core.domain.dtos.orden_compra_dtos import (
    ObtenerInfoOCQuery,
    ResultadoObtenerInfoOC,
)


class OrdenesCompraQueryPort(ABC):
    """
    Puerto para consultas especializadas de órdenes de compra.

    Responsabilidad: Consultas complejas para generación de órdenes.
    """

    @abstractmethod
    def obtener_info_oc(self, query: ObtenerInfoOCQuery) -> List[ResultadoObtenerInfoOC]:
        """
        Obtiene información de productos para generar orden de compra.

        Esta consulta agrupa productos por contacto de proveedor y retorna
        toda la información necesaria para generar las órdenes de compra.

        Args:
            query: Query del dominio con los criterios de búsqueda

        Returns:
            List[ResultadoObtenerInfoOC]: Resultados agrupados por contacto

        Raises:
            DatosInsuficientesError: Si no hay datos para los criterios especificados
        """
        pass
