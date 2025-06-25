"""
Caso de uso: Obtener Productos
"""
from typing import List, Optional

from app.core.domain.entities.product import Product
from app.core.ports.repositories.product_repository import ProductRepositoryPort


class GetProductsUseCase:
    """
    Caso de uso para obtener productos
    
    Este caso de uso encapsula la lógica de negocio para obtener productos
    con diferentes criterios de filtrado y búsqueda.
    """
    
    def __init__(self, product_repository: ProductRepositoryPort):
        """
        Inicializar el caso de uso
        
        Args:
            product_repository: Repositorio de productos (puerto)
        """
        self._product_repository = product_repository
    
    async def execute(self, skip: int = 0, limit: int = 100, 
                     active_only: bool = True) -> List[Product]:
        """
        Ejecutar el caso de uso para obtener todos los productos
        
        Args:
            skip: Número de elementos a saltar para paginación
            limit: Número máximo de elementos a devolver
            active_only: Si solo mostrar productos activos
            
        Returns:
            Lista de productos
        """
        return await self._product_repository.get_all(skip=skip, limit=limit, active_only=active_only)
    
    async def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Obtener un producto por su ID
        
        Args:
            product_id: ID del producto
            
        Returns:
            Producto si existe, None en caso contrario
        """
        return await self._product_repository.get_by_id(product_id)
    
    async def get_by_category(self, category: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Obtener productos por categoría
        
        Args:
            category: Categoría de productos
            skip: Número de elementos a saltar
            limit: Número máximo de elementos a devolver
            
        Returns:
            Lista de productos de la categoría
        """
        return await self._product_repository.get_by_category(
            category=category.strip(), skip=skip, limit=limit
        )
    
    async def search_products(self, query: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Buscar productos por nombre o descripción
        
        Args:
            query: Término de búsqueda
            skip: Número de elementos a saltar
            limit: Número máximo de elementos a devolver
            
        Returns:
            Lista de productos que coinciden con la búsqueda
        """
        if not query or len(query.strip()) < 2:
            raise ValueError("El término de búsqueda debe tener al menos 2 caracteres")
        
        return await self._product_repository.search(
            query=query.strip(), skip=skip, limit=limit
        )
    
    async def get_low_stock_products(self, threshold: int = 10) -> List[Product]:
        """
        Obtener productos con stock bajo
        
        Args:
            threshold: Umbral de stock bajo
            
        Returns:
            Lista de productos con stock bajo
        """
        if threshold < 0:
            raise ValueError("El umbral de stock debe ser mayor o igual a cero")
        
        return await self._product_repository.get_low_stock_products(threshold) 