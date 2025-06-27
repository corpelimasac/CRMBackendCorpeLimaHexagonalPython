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
    id_contacto_proveedor: list[int] = Field(
        ..., 
        description="ID del contacto del proveedor",
        example=[15, 16],
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id_cotizacion": 38,
                "id_version": 98,
                "id_contacto_proveedor": [15, 16]
            }
        }


class ProductoOCData(BaseModel):
    """
    DTO para los datos de un producto en la OC
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
    ##datos: List[ProductoOCData] = Field(..., description="Lista de productos en la OC")
    total_registros: int = Field(..., description="Total de registros encontrados")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "OC generada correctamente",
                "datos": [
                    {
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