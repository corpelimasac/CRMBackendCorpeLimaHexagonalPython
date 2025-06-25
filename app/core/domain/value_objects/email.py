"""
Value Object Email
"""
import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Email:
    """
    Value Object para representar un email
    
    Los value objects son inmutables y se identifican por su valor,
    no por su identidad.
    """
    value: str
    
    def __post_init__(self):
        """
        Validaciones posteriores a la inicialización
        """
        if not self.value:
            raise ValueError("El email no puede estar vacío")
        
        if not self.is_valid():
            raise ValueError(f"Email inválido: {self.value}")
    
    def is_valid(self) -> bool:
        """
        Validar el formato del email
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, self.value))
    
    def get_domain(self) -> str:
        """
        Obtener el dominio del email
        """
        if not self.is_valid():
            raise ValueError("Email inválido")
        
        return self.value.split('@')[1]
    
    def get_local_part(self) -> str:
        """
        Obtener la parte local del email (antes del @)
        """
        if not self.is_valid():
            raise ValueError("Email inválido")
        
        return self.value.split('@')[0]
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Email):
            return False
        return self.value.lower() == other.value.lower()
    
    def __hash__(self) -> int:
        return hash(self.value.lower()) 