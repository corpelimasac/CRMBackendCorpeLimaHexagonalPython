from pydantic import BaseModel, Field
from typing import List, Optional


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
  ptotal: float = Field(..., description="Total del producto")
  igv: Optional[str] = Field("CON IGV", description="IGV del producto (CON IGV / SIN IGV)")
  idProductoCotizacion: Optional[int] = Field(None, description="ID del producto en productos_cotizaciones")

class ProductoUpdateInfo(BaseModel):
  idOcDetalle: Optional[int] = Field(None, description="ID del detalle de la orden (null para nuevos productos)")
  idProducto: int = Field(..., description="ID del producto")
  producto: str = Field(..., description="Nombre del producto")
  marca: str = Field(..., description="Marca del producto")
  modelo: Optional[str] = Field("", description="Modelo del producto")
  unidadMedida: str = Field(..., description="Unidad de medida")
  cantidad: int = Field(..., description="Cantidad del producto")
  pUnitario: float = Field(..., description="Precio unitario del producto")
  ptotal: float = Field(..., description="Total del producto")
  igv: str = Field(..., description="IGV (CON IGV / SIN IGV)")
  eliminar: bool = Field(False, description="Si es true, marca el producto para eliminar")
  idProductoCotizacion: Optional[int] = Field(None, description="ID del producto en productos_cotizaciones")

  class Config:
    populate_by_name = True  # Permite usar tanto el nombre del campo como el alias


class Data(BaseModel):
  proveedorInfo: ProveedorInfo = Field(..., description="Información del proveedor")
  productos: list[ProductoInfo] = Field(..., description="Lista de productos")
  igv: float = Field(...,description="IGV de la OC")
  total:float=Field(...,description="Total")

## Request
class OrdenesCompraRequest(BaseModel):
  idCotizacion: int = Field(..., description="ID de la cotización")
  idCotizacionVersiones: int = Field(..., description="ID de la versión de la cotización")
  idUsuario: int = Field(..., description="ID del usuario")
  consorcio: bool = Field(..., description="Si es consorcio")
  data: List[Data] = Field(..., description="Lista de ordenes de compra")

## Response DTOs
class ProductoOrdenResponse(BaseModel):
  idOcDetalle: int = Field(..., description="ID del detalle de la orden")
  idProducto: int = Field(..., description="ID del producto")
  producto: str = Field(..., description="Nombre del producto")
  marca: str = Field(..., description="Marca del producto")
  modelo: str = Field(..., description="Modelo del producto")
  unidadMedida: str = Field(..., description="Unidad de medida")
  cantidad: int = Field(..., description="Cantidad")
  pUnitario: float = Field(..., description="Precio unitario")
  ptotal: float = Field(..., description="Precio total")
  igv: str = Field(..., description="IGV (CON IGV / SIN IGV)")

class ProveedorOrdenResponse(BaseModel):
  idProveedor: int = Field(..., description="ID del proveedor")
  razonSocial: str = Field(..., description="Razón social del proveedor")
  direccion: str = Field(..., description="Dirección del proveedor")
  idProveedorContacto: int = Field(..., description="ID del contacto")
  nombreContacto: str = Field(..., description="Nombre del contacto")
  telefono: Optional[str] = Field(None, description="Teléfono del contacto")
  celular: Optional[str] = Field(None, description="Celular del contacto")
  correo: Optional[str] = Field(None, description="Correo del contacto")

class OrdenCompraDetalleResponse(BaseModel):
  idOrden: int = Field(..., description="ID de la orden")
  numeroOc: str = Field(..., description="Número de OC")
  moneda: str = Field(..., description="Moneda")
  pago: str = Field(..., description="Forma de pago")
  total: float = Field(..., description="Total")
  entrega: Optional[str] = Field(None, description="Condiciones de entrega")
  rutaS3Antigua: Optional[str] = Field(None, description="URL del archivo en S3")
  consorcio: bool = Field(False, description="Si es consorcio")
  proveedor: ProveedorOrdenResponse = Field(..., description="Datos del proveedor")
  productos: List[ProductoOrdenResponse] = Field(..., description="Lista de productos")

## Request para actualizar orden de compra
class ActualizarOrdenCompraRequest(BaseModel):
  idOrden: int = Field(..., description="ID de la orden de compra a actualizar")
  productos: List[ProductoUpdateInfo] = Field(..., description="Lista de productos a actualizar")
  moneda: Optional[str] = Field(None, description="Moneda")
  pago: Optional[str] = Field(None, description="Forma de pago")
  entrega: Optional[str] = Field(None, description="Condiciones de entrega")
  rutaS3Antigua: Optional[str] = Field(None, description="URL del archivo S3 a eliminar")
  numeroOc: str = Field(..., description="Número de OC (correlativo) obtenido del GET")
  consorcio: bool = Field(False, description="Si es consorcio")
  igv: Optional[float] = Field(None, description="IGV de la OC (monto del IGV). Si no se envía, se calcula automáticamente")
  total: float = Field(..., description="Total de la OC")
  # Datos del proveedor para regenerar Excel
  proveedor: ProveedorOrdenResponse = Field(..., description="Datos del proveedor")