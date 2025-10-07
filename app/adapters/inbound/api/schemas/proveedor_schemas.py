# app/adapters/inbound/api/schemas/proveedor_schemas.py
from pydantic import BaseModel, Field
from typing import Optional

class ContactResponseDTO(BaseModel):
    """
    DTO para la respuesta de obtener los contactos de un proveedor
    """
    id_proveedor_contacto:int = Field(..., description="ID del contacto del proveedor")
    nombre:str = Field(..., description="Nombre del contacto del proveedor")
    telefono:Optional[int] = Field(None, description="Teléfono del contacto del proveedor")
    celular:Optional[int] = Field(None, description="Celular del contacto del proveedor")
    correo:Optional[str] = Field(None, description="Correo del contacto del proveedor")

    class Config:
        from_attributes = True 