"""
Entidad Order del dominio
"""
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum


class OrderStatus(Enum):
    """Estados de una orden"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class OrderItem:
    """
    Ítem de una orden
    """
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    
    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("La cantidad debe ser mayor que cero")
        if self.unit_price <= 0:
            raise ValueError("El precio unitario debe ser mayor que cero")
    
    @property
    def subtotal(self) -> Decimal:
        """Calcular el subtotal del ítem"""
        return self.unit_price * self.quantity


@dataclass
class Order:
    """
    Entidad Order del dominio
    
    Esta clase representa una orden en el dominio del negocio.
    Contiene las reglas de negocio y validaciones relacionadas con las órdenes.
    """
    id: Optional[int]
    user_id: int
    items: List[OrderItem] = field(default_factory=list)
    status: OrderStatus = OrderStatus.PENDING
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    
    def __post_init__(self):
        """
        Validaciones posteriores a la inicialización
        """
        if not self.items:
            raise ValueError("Una orden debe tener al menos un ítem")
        
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def add_item(self, product_id: int, product_name: str, quantity: int, unit_price: Decimal) -> None:
        """
        Agregar un ítem a la orden
        """
        if self.status != OrderStatus.PENDING:
            raise ValueError("No se pueden agregar ítems a una orden que no está pendiente")
        
        # Verificar si el producto ya existe en la orden
        for item in self.items:
            if item.product_id == product_id:
                item.quantity += quantity
                self.updated_at = datetime.utcnow()
                return
        
        # Agregar nuevo ítem
        new_item = OrderItem(product_id, product_name, quantity, unit_price)
        self.items.append(new_item)
        self.updated_at = datetime.utcnow()
    
    def remove_item(self, product_id: int) -> None:
        """
        Remover un ítem de la orden
        """
        if self.status != OrderStatus.PENDING:
            raise ValueError("No se pueden remover ítems de una orden que no está pendiente")
        
        self.items = [item for item in self.items if item.product_id != product_id]
        self.updated_at = datetime.utcnow()
        
        if not self.items:
            raise ValueError("Una orden debe tener al menos un ítem")
    
    @property
    def total_amount(self) -> Decimal:
        """Calcular el monto total de la orden"""
        return sum(item.subtotal for item in self.items)
    
    @property
    def total_items(self) -> int:
        """Calcular el total de ítems en la orden"""
        return sum(item.quantity for item in self.items)
    
    def confirm(self) -> None:
        """
        Confirmar la orden
        """
        if self.status != OrderStatus.PENDING:
            raise ValueError("Solo se pueden confirmar órdenes pendientes")
        
        self.status = OrderStatus.CONFIRMED
        self.updated_at = datetime.utcnow()
    
    def start_processing(self) -> None:
        """
        Iniciar el procesamiento de la orden
        """
        if self.status != OrderStatus.CONFIRMED:
            raise ValueError("Solo se pueden procesar órdenes confirmadas")
        
        self.status = OrderStatus.PROCESSING
        self.updated_at = datetime.utcnow()
    
    def ship(self) -> None:
        """
        Marcar la orden como enviada
        """
        if self.status != OrderStatus.PROCESSING:
            raise ValueError("Solo se pueden enviar órdenes en procesamiento")
        
        self.status = OrderStatus.SHIPPED
        self.shipped_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def deliver(self) -> None:
        """
        Marcar la orden como entregada
        """
        if self.status != OrderStatus.SHIPPED:
            raise ValueError("Solo se pueden entregar órdenes enviadas")
        
        self.status = OrderStatus.DELIVERED
        self.delivered_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def cancel(self) -> None:
        """
        Cancelar la orden
        """
        if self.status in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
            raise ValueError("No se puede cancelar una orden entregada o ya cancelada")
        
        self.status = OrderStatus.CANCELLED
        self.updated_at = datetime.utcnow()
    
    def can_be_modified(self) -> bool:
        """
        Verificar si la orden puede ser modificada
        """
        return self.status == OrderStatus.PENDING
    
    def __str__(self) -> str:
        return f"Order(id={self.id}, user_id={self.user_id}, status={self.status.value}, total={self.total_amount})" 