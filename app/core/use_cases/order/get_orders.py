"""
Caso de uso: Obtener Órdenes
"""
from typing import List, Optional
from datetime import datetime

from app.core.domain.entities.order import Order, OrderStatus
from app.core.ports.repositories.order_repository import OrderRepositoryPort


class GetOrdersUseCase:
    """
    Caso de uso para obtener órdenes
    
    Este caso de uso encapsula la lógica de negocio para obtener órdenes
    con diferentes criterios de filtrado.
    """
    
    def __init__(self, order_repository: OrderRepositoryPort):
        """
        Inicializar el caso de uso
        
        Args:
            order_repository: Repositorio de órdenes (puerto)
        """
        self._order_repository = order_repository
    
    async def execute(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """
        Ejecutar el caso de uso para obtener todas las órdenes
        
        Args:
            skip: Número de elementos a saltar para paginación
            limit: Número máximo de elementos a devolver
            
        Returns:
            Lista de órdenes
        """
        return await self._order_repository.get_all(skip=skip, limit=limit)
    
    async def get_by_id(self, order_id: int) -> Optional[Order]:
        """
        Obtener una orden por su ID
        
        Args:
            order_id: ID de la orden
            
        Returns:
            Orden si existe, None en caso contrario
        """
        return await self._order_repository.get_by_id(order_id)
    
    async def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        """
        Obtener órdenes por ID de usuario
        
        Args:
            user_id: ID del usuario
            skip: Número de elementos a saltar
            limit: Número máximo de elementos a devolver
            
        Returns:
            Lista de órdenes del usuario
        """
        return await self._order_repository.get_by_user_id(
            user_id=user_id, skip=skip, limit=limit
        )
    
    async def get_by_status(self, status: OrderStatus, skip: int = 0, limit: int = 100) -> List[Order]:
        """
        Obtener órdenes por estado
        
        Args:
            status: Estado de las órdenes
            skip: Número de elementos a saltar
            limit: Número máximo de elementos a devolver
            
        Returns:
            Lista de órdenes con el estado especificado
        """
        return await self._order_repository.get_by_status(
            status=status, skip=skip, limit=limit
        )
    
    async def get_by_date_range(self, start_date: datetime, end_date: datetime, 
                               skip: int = 0, limit: int = 100) -> List[Order]:
        """
        Obtener órdenes por rango de fechas
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            skip: Número de elementos a saltar
            limit: Número máximo de elementos a devolver
            
        Returns:
            Lista de órdenes en el rango de fechas
        """
        if start_date >= end_date:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")
        
        return await self._order_repository.get_by_date_range(
            start_date=start_date, end_date=end_date, skip=skip, limit=limit
        )
    
    async def get_pending_orders(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """
        Obtener órdenes pendientes
        
        Args:
            skip: Número de elementos a saltar
            limit: Número máximo de elementos a devolver
            
        Returns:
            Lista de órdenes pendientes
        """
        return await self._order_repository.get_pending_orders(skip=skip, limit=limit)
    
    async def get_orders_requiring_processing(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """
        Obtener órdenes que requieren procesamiento
        
        Args:
            skip: Número de elementos a saltar
            limit: Número máximo de elementos a devolver
            
        Returns:
            Lista de órdenes confirmadas listas para procesar
        """
        return await self._order_repository.get_orders_requiring_processing(skip=skip, limit=limit) 