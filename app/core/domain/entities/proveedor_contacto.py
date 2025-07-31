# app/core/domain/entities/contact.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class ProveedorContacto:
    id_proveedor_contacto: int  
    nombre: str
    telefono: Optional[int]
    celular: Optional[int]
    correo: Optional[str]
    sexo: Optional[str]
    cargo: Optional[str]
    observacion: Optional[str] 
