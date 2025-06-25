"""
Puerto del servicio de notificaciones
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class NotificationType(Enum):
    """Tipos de notificación"""
    PUSH = "push"
    SMS = "sms"
    IN_APP = "in_app"
    EMAIL = "email"


class NotificationPriority(Enum):
    """Prioridades de notificación"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class NotificationMessage:
    """
    Mensaje de notificación
    """
    recipient_id: str
    title: str
    body: str
    type: NotificationType
    priority: NotificationPriority = NotificationPriority.NORMAL
    data: Optional[Dict[str, Any]] = None
    action_url: Optional[str] = None


@dataclass
class NotificationResult:
    """
    Resultado de una notificación
    """
    message_id: str
    success: bool
    error_message: Optional[str] = None


class NotificationServicePort(ABC):
    """
    Puerto (interface) para el servicio de notificaciones
    
    Esta es una abstracción que define qué operaciones puede realizar
    el servicio de notificaciones, sin especificar cómo las implementa.
    """
    
    @abstractmethod
    async def send_notification(self, message: NotificationMessage) -> NotificationResult:
        """
        Enviar una notificación
        
        Args:
            message: Mensaje de notificación a enviar
            
        Returns:
            Resultado del envío de la notificación
        """
        pass
    
    @abstractmethod
    async def send_bulk_notification(self, messages: List[NotificationMessage]) -> List[NotificationResult]:
        """
        Enviar notificaciones en lote
        
        Args:
            messages: Lista de mensajes de notificación
            
        Returns:
            Lista de resultados del envío
        """
        pass
    
    @abstractmethod
    async def send_push_notification(self, user_id: str, title: str, body: str, 
                                   data: Optional[Dict[str, Any]] = None) -> NotificationResult:
        """
        Enviar notificación push
        
        Args:
            user_id: ID del usuario
            title: Título de la notificación
            body: Cuerpo de la notificación
            data: Datos adicionales
            
        Returns:
            Resultado del envío
        """
        pass
    
    @abstractmethod
    async def send_sms_notification(self, phone_number: str, message: str) -> NotificationResult:
        """
        Enviar notificación SMS
        
        Args:
            phone_number: Número de teléfono
            message: Mensaje a enviar
            
        Returns:
            Resultado del envío
        """
        pass
    
    @abstractmethod
    async def send_order_status_notification(self, user_id: str, order_id: int, 
                                           status: str) -> NotificationResult:
        """
        Enviar notificación de cambio de estado de orden
        
        Args:
            user_id: ID del usuario
            order_id: ID de la orden
            status: Nuevo estado de la orden
            
        Returns:
            Resultado del envío
        """
        pass
    
    @abstractmethod
    async def send_promotional_notification(self, user_ids: List[str], title: str, 
                                          body: str, action_url: Optional[str] = None) -> List[NotificationResult]:
        """
        Enviar notificación promocional a múltiples usuarios
        
        Args:
            user_ids: Lista de IDs de usuarios
            title: Título de la notificación
            body: Cuerpo de la notificación
            action_url: URL de acción opcional
            
        Returns:
            Lista de resultados del envío
        """
        pass
    
    @abstractmethod
    async def register_device_token(self, user_id: str, device_token: str, 
                                  device_type: str) -> bool:
        """
        Registrar token de dispositivo para notificaciones push
        
        Args:
            user_id: ID del usuario
            device_token: Token del dispositivo
            device_type: Tipo de dispositivo (ios, android)
            
        Returns:
            True si se registró correctamente, False en caso contrario
        """
        pass
    
    @abstractmethod
    async def unregister_device_token(self, user_id: str, device_token: str) -> bool:
        """
        Desregistrar token de dispositivo
        
        Args:
            user_id: ID del usuario
            device_token: Token del dispositivo
            
        Returns:
            True si se desregistró correctamente, False en caso contrario
        """
        pass 