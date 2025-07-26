"""
Puerto del servicio de pagos
"""
from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class PaymentStatus(Enum):
    """Estados de un pago"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


@dataclass
class PaymentMethod:
    """
    Método de pago
    """
    type: str  # "credit_card", "debit_card", "paypal", etc.
    token: str  # Token del método de pago
    last_four: Optional[str] = None  # Últimos 4 dígitos para tarjetas
    brand: Optional[str] = None  # Visa, Mastercard, etc.


@dataclass
class PaymentRequest:
    """
    Solicitud de pago
    """
    order_id: int
    amount: Decimal
    currency: str
    payment_method: PaymentMethod 
    description: Optional[str] = None


@dataclass
class PaymentResult:
    """
    Resultado de un pago
    """
    transaction_id: str
    status: PaymentStatus
    amount: Decimal
    currency: str
    message: Optional[str] = None
    gateway_response: Optional[dict] = None


class PaymentServicePort(ABC):
    """
    Puerto (interface) para el servicio de pagos
    
    Esta es una abstracción que define qué operaciones puede realizar
    el servicio de pagos, sin especificar cómo las implementa.
    """
    
    @abstractmethod
    async def process_payment(self, payment_request: PaymentRequest) -> PaymentResult:
        """
        Procesar un pago
        
        Args:
            payment_request: Solicitud de pago
            
        Returns:
            Resultado del procesamiento del pago
        """
        pass
    
    @abstractmethod
    async def refund_payment(self, transaction_id: str, amount: Optional[Decimal] = None) -> PaymentResult:
        """
        Reembolsar un pago
        
        Args:
            transaction_id: ID de la transacción a reembolsar
            amount: Monto a reembolsar (None para reembolso completo)
            
        Returns:
            Resultado del reembolso
        """
        pass
    
    @abstractmethod
    async def get_payment_status(self, transaction_id: str) -> PaymentStatus:
        """
        Obtener el estado de un pago
        
        Args:
            transaction_id: ID de la transacción
            
        Returns:
            Estado actual del pago
        """
        pass
    
    @abstractmethod
    async def validate_payment_method(self, payment_method: PaymentMethod) -> bool:
        """
        Validar un método de pago
        
        Args:
            payment_method: Método de pago a validar
            
        Returns:
            True si el método de pago es válido, False en caso contrario
        """
        pass
    
    @abstractmethod
    async def create_payment_intent(self, amount: Decimal, currency: str) -> str:
        """
        Crear una intención de pago
        
        Args:
            amount: Monto del pago
            currency: Moneda del pago
            
        Returns:
            ID de la intención de pago
        """
        pass
    
    @abstractmethod
    async def capture_payment(self, payment_intent_id: str) -> PaymentResult:
        """
        Capturar un pago previamente autorizado
        
        Args:
            payment_intent_id: ID de la intención de pago
            
        Returns:
            Resultado de la captura del pago
        """
        pass
    
    @abstractmethod
    async def cancel_payment(self, payment_intent_id: str) -> bool:
        """
        Cancelar una intención de pago
        
        Args:
            payment_intent_id: ID de la intención de pago
            
        Returns:
            True si se canceló correctamente, False en caso contrario
        """
        pass 