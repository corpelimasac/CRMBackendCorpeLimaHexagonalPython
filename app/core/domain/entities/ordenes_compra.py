from dataclasses import dataclass
from typing import List

@dataclass
class OrdenesCompraItem:
    id_producto: int
    cantidad: int
    p_unitario: float
    p_total: float

@dataclass
class OrdenesCompra:
    id_cotizacion: int
    id_version: int
    id_proveedor: int
    id_proveedor_contacto: int
    moneda: str
    pago: str
    entrega: str
    items: List[OrdenesCompraItem]