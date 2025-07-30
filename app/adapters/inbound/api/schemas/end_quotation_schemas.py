from pydantic import BaseModel, Field
"""Base modal se encarga de convertir el JSON de una petición en un objeto de Python """
"""
    El uso de Field es para indicar que el campo es requerido y el tipo de dato que debe ser
    El uso de los tres puntos (...) como primer argumento es la forma explícita 
    de decirle a Pydantic que este campo es requerido.
"""

class ProveedorInfoDTO(BaseModel):
    """
    DTO para la respuesta de obtener la informacion del proveedor
    """
    idProveedor: int = Field(..., description="ID del proveedor")
    nombreProveedor: str = Field(..., description="Nombre del proveedor")
    direccionProveedor: str = Field(..., description="Direccion del proveedor")
    moneda: str = Field(..., description="Moneda")
    entrega: str = Field(..., description="Entrega")
    pago: str = Field(..., description="Pago")


class ProductoDTO(BaseModel):
    """DTO para un único producto en la lista."""
    id: int = Field(..., description="ID del producto") 
    cant: int = Field(..., description="Cantidad del producto")
    und: str = Field(..., description="Unidad de medida")
    nombre: str = Field(..., description="Nombre del producto")
    marca: str = Field(..., description="Marca del producto")
    modelo: str = Field(..., description="Modelo del producto")
    punitario: float = Field(..., description="Precio unitario")
    ptotal: float = Field(..., description="Precio total")

class GetDataEndQuotationDTO(BaseModel):
    """
    DTO para la respuesta de obtener la informacion de la cotizacion finalizada
    """
    proveedorInfo: list[ProveedorInfoDTO] = Field(..., description="Información del proveedor")
    productos: list[ProductoDTO] = Field(..., description="Lista de productos")

    

class GetDataEndQuotationResponse(BaseModel):
    """
    DTO para la respuesta de obtener la informacion de la cotizacion finalizada
    """
    success: bool = Field(..., description="Estado de la respuesta")
    message: str = Field(..., description="Mensaje de respuesta")
    data: list[GetDataEndQuotationDTO] = Field(..., description="Datos de la cotizacion finalizada")
    class Config:
        """
        Configuracion para el ejemplo de la respuesta
        """
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Informacion de la cotizacion finalizada obtenida correctamente",
                "data": [
                    {
                        "proveedorInfo": [
                            {
                                "idProveedor": 1,
                                "nombreProveedor": "Proveedor 1",
                                "direccionProveedor": "Calle 123",
                                "moneda": "DOLARES",
                                "entrega": "10 dias",
                                "pago": "EN EFECTIVO",
                            }
                        ],
                        "productos": [
                            {
                                "id": 1,
                                "und": "UNIDAD",

                                "nombre": "Producto 1",
                                "marca": "MARCA 1",
                                "modelo": "MODELO 1",
                                "punitario": 100,
                                "ptotal": 100,
                            }
                        ]
                    }
                ]
            }
        }









    