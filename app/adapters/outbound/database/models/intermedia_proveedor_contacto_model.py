from sqlalchemy import Table, Column, Integer, ForeignKey
from .base import Base

# diagrama: Base.metadata es un MetaData
intermedia_proveedor_contacto: Table = Table(
    'intermedia_proveedor_contacto',
    Base.metadata,
    Column(
        'id_proveedor',
        Integer,
        ForeignKey('proveedores.id_proveedor'),
        primary_key=True,
    ),
    Column(
        'id_proveedor_contacto',
        Integer,
        ForeignKey('proveedor_contactos.id_proveedor_contacto'),
        primary_key=True,
    ),
)
