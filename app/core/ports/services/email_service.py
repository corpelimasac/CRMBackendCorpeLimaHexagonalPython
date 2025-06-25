"""
Puerto del servicio de email
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class EmailMessage:
    """
    Mensaje de email
    """
    to: List[str]
    subject: str
    body: str
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    html_body: Optional[str] = None
    attachments: Optional[List[str]] = None


class EmailServicePort(ABC):
    """
    Puerto (interface) para el servicio de email
    
    Esta es una abstracción que define qué operaciones puede realizar
    el servicio de email, sin especificar cómo las implementa.
    """
    
    @abstractmethod
    async def send_email(self, message: EmailMessage) -> bool:
        """
        Enviar un email
        
        Args:
            message: Mensaje de email a enviar
            
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        pass
    
    @abstractmethod
    async def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """
        Enviar email de bienvenida a un nuevo usuario
        
        Args:
            user_email: Email del usuario
            user_name: Nombre del usuario
            
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        pass
    
    @abstractmethod
    async def send_order_confirmation(self, user_email: str, order_id: int, order_total: str) -> bool:
        """
        Enviar email de confirmación de orden
        
        Args:
            user_email: Email del usuario
            order_id: ID de la orden
            order_total: Total de la orden
            
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        pass
    
    @abstractmethod
    async def send_order_shipped(self, user_email: str, order_id: int, tracking_number: str) -> bool:
        """
        Enviar email notificando que la orden ha sido enviada
        
        Args:
            user_email: Email del usuario
            order_id: ID de la orden
            tracking_number: Número de seguimiento
            
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        pass
    
    @abstractmethod
    async def send_password_reset(self, user_email: str, reset_token: str) -> bool:
        """
        Enviar email para resetear contraseña
        
        Args:
            user_email: Email del usuario
            reset_token: Token de reseteo
            
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        pass
    
    @abstractmethod
    async def send_low_stock_alert(self, admin_emails: List[str], product_name: str, current_stock: int) -> bool:
        """
        Enviar alerta de stock bajo a administradores
        
        Args:
            admin_emails: Lista de emails de administradores
            product_name: Nombre del producto con stock bajo
            current_stock: Stock actual
            
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        pass
    
    @abstractmethod
    async def validate_email_address(self, email: str) -> bool:
        """
        Validar una dirección de email
        
        Args:
            email: Dirección de email a validar
            
        Returns:
            True si la dirección es válida, False en caso contrario
        """
        pass 