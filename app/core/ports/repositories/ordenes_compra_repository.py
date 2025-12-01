"""
Puerto principal de órdenes de compra.

Este puerto hereda de los puertos especializados siguiendo el principio
de segregación de interfaces (ISP) mientras mantiene compatibilidad hacia atrás.

NOTA: Se recomienda usar los puertos especializados directamente en lugar de este:
- OrdenesCompraWritePort: Para escritura
- OrdenesCompraReadPort: Para lectura
- OrdenesCompraTransactionPort: Para transacciones
- OrdenesCompraQueryPort: Para consultas especializadas
"""
from abc import ABC, abstractmethod
from typing import List

from app.core.domain.entities.ordenes_compra import OrdenesCompra
from app.core.ports.repositories.ordenes_compra_write_port import OrdenesCompraWritePort
from app.core.ports.repositories.ordenes_compra_read_port import OrdenesCompraReadPort
from app.core.ports.repositories.ordenes_compra_transaction_port import OrdenesCompraTransactionPort
from app.core.ports.repositories.ordenes_compra_query_port import OrdenesCompraQueryPort


class OrdenesCompraRepositoryPort(
    OrdenesCompraWritePort,
    OrdenesCompraReadPort,
    OrdenesCompraTransactionPort,
    OrdenesCompraQueryPort,
    ABC
):
    """
    Puerto principal para repositorio de órdenes de compra.

    Este puerto combina todos los puertos especializados para mantener
    compatibilidad hacia atrás con código existente.

    DEPRECADO: Se recomienda usar los puertos especializados directamente.
    """

    @abstractmethod
    def save(self, order: OrdenesCompra) -> OrdenesCompra:
        """
        Guarda una orden de compra en la base de datos.

        DEPRECADO: Usar save_batch() en su lugar para evitar múltiples eventos.

        Args:
            order: Entidad de orden de compra

        Returns:
            OrdenesCompra: Orden guardada

        Raises:
            OrdenCompraError: Si hay error en la persistencia
        """
        pass

    @abstractmethod
    def save_batch(self, orders: List[OrdenesCompra]) -> List[OrdenesCompra]:
        """
        Guarda múltiples órdenes de compra en una sola transacción.

        DEPRECADO: Usar save_batch_sin_commit() + commit_con_evento() para mejor control.

        Args:
            orders: Lista de órdenes a guardar

        Returns:
            List[OrdenesCompra]: Órdenes guardadas

        Raises:
            OrdenCompraError: Si hay error en la persistencia
        """
        pass
