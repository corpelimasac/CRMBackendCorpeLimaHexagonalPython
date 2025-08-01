from pydantic import BaseModel, Field
from typing import Optional, List






class ProveedorInfo(BaseModel):
  idProveedor: int = Field(..., description="ID del proveedor")
  idProveedorContacto: int = Field(..., description="ID del contacto del proveedor")
  moneda: str = Field(..., description="Nombre del contacto del proveedor")
  pago: str = Field(..., description="Teléfono del contacto del proveedor")
  entrega: str = Field(..., description="Teléfono del contacto del proveedor")

class ProductoInfo(BaseModel):
  idProducto: int = Field(..., description="ID del producto")
  cantidad: int = Field(..., description="Cantidad del producto")
  pUnitario: float = Field(..., description="Precio unitario del producto")
  total: float = Field(..., description="Total del producto")


class Data(BaseModel):
  proveedor: ProveedorInfo = Field(..., description="Información del proveedor")
  productos: list[ProductoInfo] = Field(..., description="Lista de productos")

## Request
class OrdenesCompraRequest(BaseModel):
  idCotizacion: int = Field(..., description="ID de la cotización")
  idVersion: int = Field(..., description="ID de la versión de la cotización")
  data: List[Data] = Field(..., description="Lista de ordenes de compra")