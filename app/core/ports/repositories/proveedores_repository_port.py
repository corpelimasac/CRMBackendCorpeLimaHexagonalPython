from abc import ABC, abstractmethod
from typing import List
from app.core.domain.entities.proveedor_contacto import ProveedorContacto

class ProveedoresRepositoryPort(ABC):
    """Puerto para el repositorio de proveedores"""
    
    @abstractmethod
    def obtener_contacto_proveedor(self, id_proveedor: int) -> List[ProveedorContacto]:
        """Obtiene los datos de los contactos de un proveedor desde la persistencia."""
    