"""
DTOs del dominio para Productos de Cotización.

Estos DTOs tienen tipado fuerte y son independientes de frameworks.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class ProductoCotizacionDisponible:
    """
    Producto de cotización disponible para generar orden de compra.

    Representa un producto que aún no tiene orden de compra activa asociada.
    """
    # IDs de relación
    id_producto_cotizacion: int
    id_proveedor: int
    id_producto: int

    # Datos del proveedor
    razon_social: str
    direccion: Optional[str]
    entrega: Optional[str]
    pago: Optional[str]
    moneda: str  # 'SOLES' o 'DOLARES'

    # Datos del producto
    cantidad: int
    unidad_medida: str
    producto: str
    marca: Optional[str]
    modelo: Optional[str]

    # Precios
    precio_unitario: Decimal
    igv: str  # 'CON IGV' o 'SIN IGV'
    precio_total: Decimal


@dataclass
class ProductoCotizacionInfo:
    """
    Información básica de un producto en una cotización.

    Usado para consultas generales de productos.
    """
    id_producto_cotizacion: int
    id_producto: int
    nombre_producto: str
    cantidad: int
    precio_unitario: Decimal
    precio_total: Decimal
    igv: str
    marca: Optional[str]
    modelo: Optional[str]
    unidad_medida: Optional[str]
