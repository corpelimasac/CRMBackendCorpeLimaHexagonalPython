"""
Puerto del repositorio de productos
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from app.core.domain.entities.product import Product


class ProductRepositoryPort(ABC):
    """
    Puerto (interface) para el repositorio de productos
    
    Esta es una abstracción que define qué operaciones puede realizar
    el repositorio de productos, sin especificar cómo las implementa.
    """
    
    @abstractmethod
    async def create(self, product: Product) -> Product:
        """
        Crear un nuevo producto
        
        Args:
            product: Producto a crear
            
        Returns:
            Producto creado con ID asignado
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Obtener un producto por su ID
        
        Args:
            product_id: ID del producto
            
        Returns:
            Producto si existe, None en caso contrario
        """
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Product]:
        """
        Obtener un producto por su nombre
        
        Args:
            name: Nombre del producto
            
        Returns:
            Producto si existe, None en caso contrario
        """
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[Product]:
        """
        Obtener todos los productos con paginación
        
        Args:
            skip: Número de elementos a saltar
            limit: Número máximo de elementos a devolver
            active_only: Si solo mostrar productos activos
            
        Returns:
            Lista de productos
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def search(self, query: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Buscar productos por nombre o descripción
        
        Args:
            query: Término de búsqueda
            skip: Número de elementos a saltar
            limit: Número máximo de elementos a devolver
            
        Returns:
            Lista de productos que coinciden con la búsqueda
        """
        pass
    
    @abstractmethod
    async def update(self, product: Product) -> Product:
        """
        Actualizar un producto existente
        
        Args:
            product: Producto con datos actualizados
            
        Returns:
            Producto actualizado
        """
        pass
    
    @abstractmethod
    async def delete(self, product_id: int) -> bool:
        """
        Eliminar un producto por su ID
        
        Args:
            product_id: ID del producto a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        pass
    
    @abstractmethod
    async def update_stock(self, product_id: int, quantity: int) -> Product:
        """
        Actualizar el stock de un producto
        
        Args:
            product_id: ID del producto
            quantity: Cantidad a agregar/quitar del stock (puede ser negativa)
            
        Returns:
            Producto con stock actualizado
        """
        pass
    
    @abstractmethod
    async def get_low_stock_products(self, threshold: int = 10) -> List[Product]:
        """
        Obtener productos con stock bajo
        
        Args:
            threshold: Umbral de stock bajo
            
        Returns:
            Lista de productos con stock bajo
        """
        pass
    
    @abstractmethod
    async def exists_by_name(self, name: str) -> bool:
        """
        Verificar si existe un producto con el nombre dado
        
        Args:
            name: Nombre a verificar
            
        Returns:
            True si existe, False en caso contrario
        """
        pass 