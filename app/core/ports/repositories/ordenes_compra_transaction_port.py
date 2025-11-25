"""
Puerto para control transaccional de órdenes de compra.

Este puerto sigue el principio de segregación de interfaces (ISP).
"""
from abc import ABC, abstractmethod
from typing import List

from app.core.domain.entities.ordenes_compra import OrdenesCompra


class OrdenesCompraTransactionPort(ABC):
    """
    Puerto para control transaccional de órdenes de compra.

    Responsabilidad: Gestión de transacciones y eventos.
    """

    @abstractmethod
    def commit_con_evento(self, orders: List[OrdenesCompra]) -> None:
        """
        Hace commit de todas las operaciones pendientes y encola el evento.

        Este método implementa el patrón Transactional Event Listener:
        - Confirma la transacción
        - Encola evento para procesamiento asíncrono DESPUÉS del commit exitoso
        - Si falla el commit, NO se dispara el evento

        Args:
            orders: Lista de órdenes para incluir en el evento

        Raises:
            OrdenCompraError: Si hay error en el commit
        """
        pass

    @abstractmethod
    def rollback(self) -> None:
        """
        Hace rollback de todas las operaciones pendientes.

        Deshace todos los cambios no confirmados en la sesión actual.
        """
        pass
