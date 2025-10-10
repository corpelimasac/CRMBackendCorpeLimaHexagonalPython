"""
Entidad User del dominio
"""
from datetime import datetime
from typing import Optional, Union
from dataclasses import dataclass
from app.core.domain.value_objects.email import Email


@dataclass
class User:
    """
    Entidad User del dominio
    
    Esta clase representa un usuario en el dominio del negocio.
    Contiene las reglas de negocio y validaciones relacionadas con los usuarios.
    """
    id: Optional[int]
    name: str
    email: Union[Email, str]
    phone: Optional[str]
    is_active: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    def __post_init__(self):
        """
        Validaciones posteriores a la inicialización
        """
        if not self.name or len(self.name.strip()) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres")
        
        if isinstance(self.email, str):
            self.email = Email(self.email)
    
    def activate(self) -> None:
        """
        Activar el usuario
        """
        self.is_active = True
        self.updated_at = datetime.now()
    
    def deactivate(self) -> None:
        """
        Desactivar el usuario
        """
        self.is_active = False
        self.updated_at = datetime.now()
    
    def update_profile(self, name: Optional[str] = None, phone: Optional[str] = None) -> None:
        """
        Actualizar el perfil del usuario
        """
        if name and len(name.strip()) >= 2:
            self.name = name.strip()
        
        if phone is not None:
            self.phone = phone
        
        self.updated_at = datetime.now()
    
    def can_place_order(self) -> bool:
        """
        Verificar si el usuario puede realizar pedidos
        """
        return self.is_active and self.email.is_valid()
    
    def __str__(self) -> str:
        return f"User(id={self.id}, name='{self.name}', email='{self.email.value}')" 