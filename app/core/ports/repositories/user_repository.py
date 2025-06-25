"""
Puerto del repositorio de usuarios
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from app.core.domain.entities.user import User


class UserRepositoryPort(ABC):
    """
    Puerto (interface) para el repositorio de usuarios
    
    Esta es una abstracción que define qué operaciones puede realizar
    el repositorio de usuarios, sin especificar cómo las implementa.
    """
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """
        Crear un nuevo usuario
        
        Args:
            user: Usuario a crear
            
        Returns:
            Usuario creado con ID asignado
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Obtener un usuario por su ID
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Usuario si existe, None en caso contrario
        """
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Obtener un usuario por su email
        
        Args:
            email: Email del usuario
            
        Returns:
            Usuario si existe, None en caso contrario
        """
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Obtener todos los usuarios con paginación
        
        Args:
            skip: Número de elementos a saltar
            limit: Número máximo de elementos a devolver
            
        Returns:
            Lista de usuarios
        """
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """
        Actualizar un usuario existente
        
        Args:
            user: Usuario con datos actualizados
            
        Returns:
            Usuario actualizado
        """
        pass
    
    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """
        Eliminar un usuario por su ID
        
        Args:
            user_id: ID del usuario a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """
        Verificar si existe un usuario con el email dado
        
        Args:
            email: Email a verificar
            
        Returns:
            True si existe, False en caso contrario
        """
        pass 