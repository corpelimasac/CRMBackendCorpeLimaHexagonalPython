from abc import ABC, abstractmethod
from typing import List, Optional
from app.adapters.outbound.database.models.registro_compra_model import RegistroCompraModel
from app.adapters.outbound.database.models.ordenes_compra_model import OrdenesCompraModel


class RegistroCompraRepositoryPort(ABC):
    """
    Port para el repositorio de registro de compras
    """

    @abstractmethod
    def obtener_por_cotizacion(self, id_cotizacion: int, id_cotizacion_versiones: int = None) -> Optional[RegistroCompraModel]:
        """
        Obtiene el registro de compra asociado a una cotización y versión

        Args:
            id_cotizacion: ID de la cotización
            id_cotizacion_versiones: ID de la versión de la cotización (opcional)

        Returns:
            RegistroCompraModel: Registro encontrado o None
        """
        pass

    @abstractmethod
    def obtener_ordenes_por_cotizacion(self, id_cotizacion: int, id_cotizacion_versiones: int = None) -> List[OrdenesCompraModel]:
        """
        Obtiene todas las órdenes de compra de una cotización y versión específica

        Args:
            id_cotizacion: ID de la cotización
            id_cotizacion_versiones: ID de la versión de la cotización (opcional)

        Returns:
            List[OrdenesCompraModel]: Lista de órdenes de compra
        """
        pass

    @abstractmethod
    def guardar_o_actualizar(self, id_cotizacion: int, ordenes: List[OrdenesCompraModel], datos_calculados: dict, id_cotizacion_versiones: int = None) -> RegistroCompraModel:
        """
        Guarda o actualiza un registro de compra con sus órdenes

        Args:
            id_cotizacion: ID de la cotización
            ordenes: Lista de órdenes de compra
            datos_calculados: Diccionario con montos calculados
            id_cotizacion_versiones: ID de la versión de la cotización (opcional)

        Returns:
            RegistroCompraModel: Registro guardado/actualizado
        """
        pass

    @abstractmethod
    def eliminar_orden_de_registro(self, compra_id: int, id_orden: int):
        """
        Elimina una orden específica de un registro de compra

        Args:
            compra_id: ID del registro de compra
            id_orden: ID de la orden a eliminar
        """
        pass

    @abstractmethod
    def eliminar_registro(self, compra_id: int):
        """
        Elimina un registro de compra completo

        Args:
            compra_id: ID del registro de compra
        """
        pass
