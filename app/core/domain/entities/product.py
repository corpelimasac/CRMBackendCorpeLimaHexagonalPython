"""
Entidad Product del dominio
"""
from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Product:
    """
    Entidad Product del dominio
    
    Esta clase representa un producto en el dominio del negocio.
    Contiene las reglas de negocio y validaciones relacionadas con los productos.
    """
    id: Optional[int]
    name: str
    description: Optional[str]
    price: Decimal
    stock: int
    category: str
    is_active: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    def __post_init__(self):
        """
        Validaciones posteriores a la inicialización
        """
        if not self.name or len(self.name.strip()) < 2:
            raise ValueError("El nombre del producto debe tener al menos 2 caracteres")
        
        if self.price <= 0:
            raise ValueError("El precio debe ser mayor que cero")
        
        if self.stock < 0:
            raise ValueError("El stock no puede ser negativo")
    
    def update_stock(self, quantity: int) -> None:
        """
        Actualizar el stock del producto
        """
        new_stock = self.stock + quantity
        if new_stock < 0:
            raise ValueError("Stock insuficiente")
        
        self.stock = new_stock
        self.updated_at = datetime.now()
    
    def update_price(self, new_price: Decimal) -> None:
        """
        Actualizar el precio del producto
        """
        if new_price <= 0:
            raise ValueError("El precio debe ser mayor que cero")
        
        self.price = new_price
        self.updated_at = datetime.now()
    
    def activate(self) -> None:
        """
        Activar el producto
        """
        self.is_active = True
        self.updated_at = datetime.now()
    
    def deactivate(self) -> None:
        """
        Desactivar el producto
        """
        self.is_active = False
        self.updated_at = datetime.now()
    
    def is_available(self) -> bool:
        """
        Verificar si el producto está disponible para la venta
        """
        return self.is_active and self.stock > 0
    
    def can_fulfill_order(self, quantity: int) -> bool:
        """
        Verificar si se puede cumplir con una orden de cierta cantidad
        """
        return self.is_available() and self.stock >= quantity
    
    def __str__(self) -> str:
        return f"Product(id={self.id}, name='{self.name}', price={self.price}, stock={self.stock})" 