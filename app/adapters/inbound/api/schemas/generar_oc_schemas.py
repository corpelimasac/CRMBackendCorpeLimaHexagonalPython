"""
Esquemas Pydantic para el endpoint de generar OC
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class GenerarOCRequest(BaseModel):
    """
    DTO para la solicitud de generar OC
    """
    id_cotizacion: int = Field(
        ..., 
        description="ID de la cotización",
        example=38,
        gt=0
    )
    id_version: int = Field(
        ..., 
        description="ID de la versión de la cotización",
        example=98,
        gt=0
    )
    id_contacto_proveedor: List[int] = Field(
        ...,
        description="ID del contacto del proveedor",
        example=[13, 14],
    )
    id_usuario: int = Field(
        ..., 
        description="ID del usuario",
        example=1,
        gt=0
    )
    consorcio: bool = Field(
        ..., 
        description="Si es consorcio",
        example=True
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_cotizacion": 38,
                "id_version": 98,
                "id_contacto_proveedor": [13, 14],
                "id_usuario": 8,
                "consorcio": True
            }
        }


class ProductoOCData(BaseModel):
    """
    DTO para los datos de un producto en la OC
    """
    
    """
    El uso de Field es para indicar que el campo es requerido y el tipo de dato que debe ser
    El uso de los tres puntos (...) como primer argumento es la forma explícita 
    de decirle a Pydantic que este campo es requerido.
    """
    IDCOTIZACION: int = Field(..., description="ID de la cotización")
    IDVERSION: int = Field(..., description="ID de la versión")
    CANT: Optional[int] = Field(None, description="Cantidad del producto")
    UMED: Optional[str] = Field(None, description="Unidad de medida")
    PRODUCTO: Optional[str] = Field(None, description="Nombre del producto")
    MARCA: Optional[str] = Field(None, description="Marca del producto")
    MODELO: Optional[str] = Field(None, description="Modelo del producto")
    FECHA: Optional[date] = Field(None, description="Fecha de modificación")
    IDPROVEEDOR: Optional[int] = Field(None, description="ID del proveedor")
    PROVEEDOR: Optional[str] = Field(None, description="Razón social del proveedor")
    IDPROVEEDORCONTACTO: Optional[int] = Field(None, description="ID del contacto del proveedor")
    PERSONAL: Optional[str] = Field(None, description="Nombre del personal de contacto")
    TELEFONO: Optional[str] = Field(None, description="Teléfono del contacto")
    CELULAR: Optional[str] = Field(None, description="Celular del contacto")
    CORREO: Optional[str] = Field(None, description="Correo del contacto")
    DIRECCION: Optional[str] = Field(None, description="Dirección del proveedor")
    MONEDA: Optional[str] = Field(None, description="Moneda (SOLES/DOLARES)")
    PAGO: Optional[str] = Field(None, description="Condiciones de pago")
    PUNIT: Optional[float] = Field(None, description="Precio unitario")
    IGV: Optional[str] = Field(None, description="IGV")

    class Config:
        json_schema_extra = {
            "example": {
                "IDCOTIZACION": 38,
                "IDVERSION": 98,
                "CANT": 5,
                "UMED": "UNIDADES",
                "PRODUCTO": "Laptop Dell Inspiron",
                "MARCA": "Dell",
                "MODELO": "Inspiron 15",
                "FECHA": "2024-01-15",
                "IDPROVEEDOR": 1,
                "PROVEEDOR": "Tecnología ABC S.A.",
                "IDPROVEEDORCONTACTO": 15,
                "PERSONAL": "Juan Pérez",
                "TELEFONO": "01-1234567",
                "CELULAR": "999888777",
                "CORREO": "juan.perez@abc.com",
                "DIRECCION": "Av. Principal 123, Lima",
                "MONEDA": "SOLES",
                "PAGO": "30 días",
                "PUNIT": 2500.00,
                "IGV": "18%"
            }
        }


class GenerarOCResponse(BaseModel):
    """
    DTO para la respuesta de generar OC
    """
    message: str = Field(..., description="Mensaje de respuesta")
    datos: List[str] = Field(..., description="Lista de URLs de los archivos subidos")
    total_registros: int = Field(..., description="Total de registros encontrados")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "OC generada correctamente",
                "datos": [
                    {
                        "url": "https://example.com/oc1.pdf",
                        "nombre_archivo": "OC1.pdf"
                        
                    }
                ],
                "total_registros": 1
            }
        }


class ErrorResponse(BaseModel):
    """
    DTO para respuestas de error
    """
    detail: str = Field(..., description="Descripción del error")

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Cotizacion no encontrada"
            }
        } 