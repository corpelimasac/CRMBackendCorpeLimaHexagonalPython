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
    id_usuario: int
    id_cotizacion: int
    id_cotizacion_versiones: int
    id_proveedor: int
    id_proveedor_contacto: int
    moneda: str
    pago: str
    entrega: str
    consorcio: bool
    items: List[OrdenesCompraItem]