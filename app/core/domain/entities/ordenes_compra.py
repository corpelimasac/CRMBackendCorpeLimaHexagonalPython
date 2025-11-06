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
    igv: float
    total: float
    moneda: str
    pago: str
    entrega: str
    consorcio: bool
    items: List[OrdenesCompraItem]
    registro_compra_orden: object = None

    def __post_init__(self):
        if self.registro_compra_orden is None:
            self.registro_compra_orden = None