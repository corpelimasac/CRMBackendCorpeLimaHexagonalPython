"""
DTOs (Data Transfer Objects) del dominio.

Estos DTOs son independientes de cualquier adaptador o framework.
Definen contratos de datos con tipado fuerte para la comunicación
entre capas manteniendo la pureza del dominio.
"""

from .orden_compra_dtos import (
    ObtenerInfoOCQuery,
    InfoOCProducto,
    InfoOCProveedor,
    InfoOCContacto,
    OrdenCompraCompleta,
    DetalleProductoOC,
    AuditoriaOrdenCompra,
    DatosExcelOC,
    DatosOrdenExcel,
    DatosProveedorExcel,
    DatosProductoExcel,
)
from .producto_cotizacion_dtos import (
    ProductoCotizacionDisponible,
    ProductoCotizacionInfo,
)

__all__ = [
    "ObtenerInfoOCQuery",
    "InfoOCProducto",
    "InfoOCProveedor",
    "InfoOCContacto",
    "OrdenCompraCompleta",
    "DetalleProductoOC",
    "AuditoriaOrdenCompra",
    "DatosExcelOC",
    "DatosOrdenExcel",
    "DatosProveedorExcel",
    "DatosProductoExcel",
    "ProductoCotizacionDisponible",
    "ProductoCotizacionInfo",
]
