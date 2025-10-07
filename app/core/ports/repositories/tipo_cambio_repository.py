from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional
from datetime import date


class TipoCambioRepositoryPort(ABC):
    """
    Port para el repositorio de tipo de cambio SUNAT
    """

    @abstractmethod
    def obtener_tipo_cambio_mas_reciente(self) -> Optional[Decimal]:
        """
        Obtiene el tipo de cambio (venta) más reciente de SUNAT

        Returns:
            Decimal: Tipo de cambio venta, None si no hay datos
        """
        pass

    @abstractmethod
    def obtener_tipo_cambio_por_fecha(self, fecha: date) -> Optional[Decimal]:
        """
        Obtiene el tipo de cambio (venta) para una fecha específica

        Args:
            fecha: Fecha del tipo de cambio

        Returns:
            Decimal: Tipo de cambio venta, None si no hay datos
        """
        pass
