"""
Caso de uso: Crear Orden
"""
from typing import List, Dict
from decimal import Decimal

from app.core.domain.entities.order import Order, OrderItem
from app.core.domain.entities.product import Product
from app.core.ports.repositories.order_repository import OrderRepositoryPort
from app.core.ports.repositories.product_repository import ProductRepositoryPort
from app.core.ports.services.email_service import EmailServicePort
from app.core.ports.services.notification_service import NotificationServicePort
from app.core.domain.exceptions.business_exceptions import InsufficientStockError, ProductNotFoundError


class CreateOrderUseCase:
    """
    Caso de uso para crear una nueva orden
    
    Este caso de uso encapsula la lógica de negocio para crear órdenes,
    incluyendo validaciones de stock, cálculos de precios y notificaciones.
    """
    
    def __init__(
        self, 
        order_repository: OrderRepositoryPort,
        product_repository: ProductRepositoryPort,
        email_service: EmailServicePort,
        notification_service: NotificationServicePort
    ):
        """
        Inicializar el caso de uso
        
        Args:
            order_repository: Repositorio de órdenes
            product_repository: Repositorio de productos
            email_service: Servicio de email
            notification_service: Servicio de notificaciones
        """
        self._order_repository = order_repository
        self._product_repository = product_repository
        self._email_service = email_service
        self._notification_service = notification_service
    
    async def execute(self, user_id: int, user_email: str, 
                     items: List[Dict[str, int]]) -> Order:
        """
        Ejecutar el caso de uso para crear una orden
        
        Args:
            user_id: ID del usuario que hace la orden
            user_email: Email del usuario
            items: Lista de ítems con product_id y quantity
            
        Returns:
            Orden creada
            
        Raises:
            ProductNotFoundError: Si un producto no existe
            InsufficientStockError: Si no hay stock suficiente
            ValueError: Si los datos de entrada son inválidos
        """
        if not items:
            raise ValueError("La orden debe tener al menos un ítem")
        
        # Validar y obtener productos
        order_items = []
        for item_data in items:
            product_id = item_data.get('product_id')
            quantity = item_data.get('quantity')
            
            if not product_id or quantity <= 0:
                raise ValueError("Cada ítem debe tener product_id y quantity válidos")
            
            # Obtener el producto
            product = await self._product_repository.get_by_id(product_id)
            if not product:
                raise ProductNotFoundError(f"Producto con ID {product_id} no encontrado")
            
            # Verificar disponibilidad
            if not product.can_fulfill_order(quantity):
                raise InsufficientStockError(
                    f"Stock insuficiente para el producto {product.name}. "
                    f"Solicitado: {quantity}, Disponible: {product.stock}"
                )
            
            # Crear ítem de orden
            order_item = OrderItem(
                product_id=product.id,
                product_name=product.name,
                quantity=quantity,
                unit_price=product.price
            )
            order_items.append(order_item)
        
        # Crear la orden
        order = Order(
            id=None,
            user_id=user_id,
            items=order_items
        )
        
        # Guardar la orden
        created_order = await self._order_repository.create(order)
        
        # Actualizar stock de productos
        for item in order_items:
            await self._product_repository.update_stock(
                item.product_id, -item.quantity
            )
        
        # Enviar notificaciones asíncronas
        await self._send_order_notifications(created_order, user_email)
        
        return created_order
    
    async def _send_order_notifications(self, order: Order, user_email: str):
        """
        Enviar notificaciones relacionadas con la orden
        """
        try:
            # Enviar email de confirmación
            await self._email_service.send_order_confirmation(
                user_email, order.id, str(order.total_amount)
            )
            
            # Enviar notificación push
            await self._notification_service.send_order_status_notification(
                str(order.user_id), order.id, order.status.value
            )
        except Exception as e:
            # Log del error, pero no fallar la creación de la orden
            print(f"Error enviando notificaciones para orden {order.id}: {e}") 