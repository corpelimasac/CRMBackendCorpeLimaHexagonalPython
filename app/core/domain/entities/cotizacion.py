from dataclasses import dataclass
from datetime import datetime
@dataclass
class Cotizacion:
    id_cotizacion: int
    activo: bool
    fecha_actualizacion: datetime
    fecha_creacion: datetime
    id_usuario: int
    igv: float
    precio_venta: float
    id_usuario:int
    id_cliente_contacto:int
    referencia:str
    nota:str
    consorcio:bool
    