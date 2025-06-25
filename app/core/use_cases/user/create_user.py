"""
Caso de uso: Crear Usuario
"""
from datetime import datetime
from typing import Optional

from app.core.domain.entities.user import User
from app.core.domain.value_objects.email import Email
from app.core.ports.repositories.user_repository import UserRepositoryPort
from app.core.domain.exceptions.business_exceptions import UserAlreadyExistsError


class CreateUserUseCase:
    """
    Caso de uso para crear un nuevo usuario
    
    Este caso de uso encapsula la lógica de negocio para crear usuarios,
    incluyendo validaciones y reglas de negocio específicas.
    """
    
    def __init__(self, user_repository: UserRepositoryPort):
        """
        Inicializar el caso de uso
        
        Args:
            user_repository: Repositorio de usuarios (puerto)
        """
        self._user_repository = user_repository
    
    async def execute(self, name: str, email: str, phone: Optional[str] = None) -> User:
        """
        Ejecutar el caso de uso para crear un usuario
        
        Args:
            name: Nombre del usuario
            email: Email del usuario
            phone: Teléfono del usuario (opcional)
            
        Returns:
            Usuario creado
            
        Raises:
            UserAlreadyExistsError: Si ya existe un usuario con ese email
            ValueError: Si los datos de entrada son inválidos
        """
        # Validar que el email no esté ya registrado
        existing_user = await self._user_repository.get_by_email(email)
        if existing_user:
            raise UserAlreadyExistsError(f"Ya existe un usuario con el email: {email}")
        
        # Crear el value object email (validará el formato)
        email_vo = Email(email)
        
        # Crear la entidad usuario
        user = User(
            id=None,  # Se asignará por el repositorio
            name=name.strip(),
            email=email_vo,
            phone=phone.strip() if phone else None,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Guardar el usuario usando el repositorio
        created_user = await self._user_repository.create(user)
        
        return created_user 