"""
Caso de uso: Crear Producto
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal

from app.core.domain.entities.product import Product
from app.core.ports.repositories.product_repository import ProductRepositoryPort
from app.core.domain.exceptions.business_exceptions import ProductAlreadyExistsError


class CreateProductUseCase:
    """
    Caso de uso para crear un nuevo producto
    
    Este caso de uso encapsula la lógica de negocio para crear productos,
    incluyendo validaciones y reglas de negocio específicas.
    """
    
    def __init__(self, product_repository: ProductRepositoryPort):
        """
        Inicializar el caso de uso
        
        Args:
            product_repository: Repositorio de productos (puerto)
        """
        self._product_repository = product_repository
    
    async def execute(self, name: str, description: Optional[str], price: Decimal, 
                     stock: int, category: str) -> Product:
        """
        Ejecutar el caso de uso para crear un producto
        
        Args:
            name: Nombre del producto
            description: Descripción del producto
            price: Precio del producto
            stock: Stock inicial del producto
            category: Categoría del producto
            
        Returns:
            Producto creado
            
        Raises:
            ProductAlreadyExistsError: Si ya existe un producto con ese nombre
            ValueError: Si los datos de entrada son inválidos
        """
        # Validar que el nombre no esté ya registrado
        existing_product = await self._product_repository.get_by_name(name)
        if existing_product:
            raise ProductAlreadyExistsError(f"Ya existe un producto con el nombre: {name}")
        
        # Crear la entidad producto
        product = Product(
            id=None,  # Se asignará por el repositorio
            name=name.strip(),
            description=description.strip() if description else None,
            price=price,
            stock=stock,
            category=category.strip(),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Guardar el producto usando el repositorio
        created_product = await self._product_repository.create(product)
        
        return created_product 