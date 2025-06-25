"""
Value Object Money
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class Money:
    """
    Value Object para representar valores monetarios
    
    Los value objects son inmutables y se identifican por su valor,
    no por su identidad.
    """
    amount: Decimal
    currency: str = "USD"
    
    def __post_init__(self):
        """
        Validaciones posteriores a la inicialización
        """
        if not isinstance(self.amount, Decimal):
            # Convertir a Decimal si es necesario
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))
        
        if self.amount < 0:
            raise ValueError("El monto no puede ser negativo")
        
        if not self.currency or len(self.currency) != 3:
            raise ValueError("La moneda debe ser un código de 3 caracteres (ej: USD, EUR, PEN)")
        
        # Normalizar currency a mayúsculas
        object.__setattr__(self, 'currency', self.currency.upper())
    
    def add(self, other: 'Money') -> 'Money':
        """
        Sumar dos objetos Money
        """
        if self.currency != other.currency:
            raise ValueError(f"No se pueden sumar monedas diferentes: {self.currency} y {other.currency}")
        
        return Money(self.amount + other.amount, self.currency)
    
    def subtract(self, other: 'Money') -> 'Money':
        """
        Restar dos objetos Money
        """
        if self.currency != other.currency:
            raise ValueError(f"No se pueden restar monedas diferentes: {self.currency} y {other.currency}")
        
        result_amount = self.amount - other.amount
        if result_amount < 0:
            raise ValueError("El resultado de la resta no puede ser negativo")
        
        return Money(result_amount, self.currency)
    
    def multiply(self, factor: Decimal) -> 'Money':
        """
        Multiplicar el monto por un factor
        """
        if not isinstance(factor, Decimal):
            factor = Decimal(str(factor))
        
        if factor < 0:
            raise ValueError("El factor de multiplicación no puede ser negativo")
        
        return Money(self.amount * factor, self.currency)
    
    def divide(self, divisor: Decimal) -> 'Money':
        """
        Dividir el monto por un divisor
        """
        if not isinstance(divisor, Decimal):
            divisor = Decimal(str(divisor))
        
        if divisor <= 0:
            raise ValueError("El divisor debe ser mayor que cero")
        
        return Money(self.amount / divisor, self.currency)
    
    def is_zero(self) -> bool:
        """
        Verificar si el monto es cero
        """
        return self.amount == 0
    
    def is_positive(self) -> bool:
        """
        Verificar si el monto es positivo
        """
        return self.amount > 0
    
    def format(self, decimal_places: int = 2) -> str:
        """
        Formatear el monto para visualización
        """
        if self.currency == "USD":
            symbol = "$"
        elif self.currency == "EUR":
            symbol = "€"
        elif self.currency == "PEN":
            symbol = "S/"
        else:
            symbol = self.currency
        
        formatted_amount = f"{self.amount:.{decimal_places}f}"
        return f"{symbol} {formatted_amount}"
    
    def __str__(self) -> str:
        return self.format()
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency
    
    def __lt__(self, other: 'Money') -> bool:
        if self.currency != other.currency:
            raise ValueError(f"No se pueden comparar monedas diferentes: {self.currency} y {other.currency}")
        return self.amount < other.amount
    
    def __le__(self, other: 'Money') -> bool:
        if self.currency != other.currency:
            raise ValueError(f"No se pueden comparar monedas diferentes: {self.currency} y {other.currency}")
        return self.amount <= other.amount
    
    def __gt__(self, other: 'Money') -> bool:
        if self.currency != other.currency:
            raise ValueError(f"No se pueden comparar monedas diferentes: {self.currency} y {other.currency}")
        return self.amount > other.amount
    
    def __ge__(self, other: 'Money') -> bool:
        if self.currency != other.currency:
            raise ValueError(f"No se pueden comparar monedas diferentes: {self.currency} y {other.currency}")
        return self.amount >= other.amount
    
    def __hash__(self) -> int:
        return hash((self.amount, self.currency)) 