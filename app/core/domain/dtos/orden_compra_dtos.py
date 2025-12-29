"""
DTOs del dominio para Órdenes de Compra.

Estos DTOs tienen tipado fuerte y son independientes de frameworks.
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional


@dataclass
class ObtenerInfoOCQuery:
    """
    Query para obtener información de productos para generar orden de compra.

    Este DTO del dominio reemplaza la dependencia de GenerarOCRequest del adaptador.
    """
    id_usuario: int
    id_cotizacion: int
    id_version: int
    id_contacto_proveedor: List[int]
    consorcio: bool


@dataclass
class InfoOCProducto:
    """
    Información de un producto en una orden de compra.

    Representa los datos necesarios para generar la orden.
    """
    id_producto: int
    nombre_producto: str
    descripcion: Optional[str]
    cantidad: int
    precio_unitario: Decimal
    precio_total: Decimal
    igv: str  # 'CON IGV' o 'SIN IGV'
    id_producto_cotizacion: int
    marca: Optional[str]
    unidad_medida: Optional[str]
    modelo: Optional[str]


@dataclass
class InfoOCProveedor:
    """Información del proveedor en una orden de compra."""
    id_proveedor: int
    razon_social: str
    ruc: str
    direccion: Optional[str]
    telefono: Optional[str]
    email: Optional[str]


@dataclass
class InfoOCContacto:
    """Información del contacto del proveedor."""
    id_contacto: int
    nombre_completo: str
    telefono: Optional[str]
    celular: Optional[str]
    email: Optional[str]


@dataclass
class DetalleProductoOC:
    """
    Detalle de un producto en una orden de compra existente.

    Usado para consultas de órdenes existentes.
    """
    id_oc_detalle: int
    id_orden: int
    id_producto: int
    nombre_producto: str
    cantidad: int
    precio_unitario: Decimal
    precio_total: Decimal
    igv: str
    id_producto_cotizacion: Optional[int]
    marca: Optional[str]
    unidad_medida: Optional[str]
    modelo: Optional[str]


@dataclass
class OrdenCompraCompleta:
    """
    Representación completa de una orden de compra con todos sus datos.

    Usado como respuesta en queries de consulta.
    """
    # Datos de la orden
    id_orden: int
    numero_oc: str
    fecha_creacion: datetime
    moneda: str
    pago: str
    entrega: str
    igv: Decimal
    total: Decimal
    ruta_s3: Optional[str]
    consorcio: bool

    # Datos del proveedor
    proveedor: InfoOCProveedor

    # Datos del contacto
    contacto: InfoOCContacto

    # Productos
    productos: List[DetalleProductoOC]

    # Datos de cotización
    id_cotizacion: int
    id_cotizacion_versiones: int

    # Datos de usuario
    id_usuario: int


@dataclass
class AuditoriaOrdenCompra:
    """
    Registro de auditoría de una orden de compra.

    Representa cambios en el ciclo de vida de la orden.
    """
    id_auditoria: int
    id_orden_compra: int
    tipo_cambio: str  # 'CREACION', 'ACTUALIZACION', 'ELIMINACION'
    descripcion: str
    usuario: str
    fecha: datetime
    datos_anteriores: Optional[dict]
    datos_nuevos: Optional[dict]


@dataclass
class ResultadoObtenerInfoOC:
    def __init__(self):
        self.id_proveedor_contacto = None

    """
    Resultado de la consulta obtener_info_oc.

    Agrupa toda la información necesaria para generar órdenes de compra.
    """
    productos: List[InfoOCProducto]
    proveedor: InfoOCProveedor
    contacto: InfoOCContacto
    id_cotizacion: int
    id_version: int
    consorcio: bool


@dataclass
class DatosExcelOC:
    """
    Datos completos para generar un Excel de orden de compra.

    Este DTO contiene toda la información de una fila de consulta de OC
    para generación de Excel.
    """
    # Identificadores
    numero_oc: str
    id_cotizacion: int
    id_version: int
    id_proveedor: int
    id_proveedor_contacto: int

    # Datos del producto
    cantidad: int
    unidad_medida: str
    producto: str
    marca: Optional[str]
    modelo: Optional[str]
    precio_unitario: Decimal
    igv: str
    precio_total: Decimal

    # Datos del proveedor
    proveedor: str
    direccion: Optional[str]

    # Datos del contacto
    personal: Optional[str]
    telefono: Optional[str]
    celular: Optional[str]
    correo: Optional[str]

    # Datos de la orden
    fecha: datetime
    moneda: str
    pago: str


@dataclass
class DatosOrdenExcel:
    """Datos de la orden para generación de Excel directa."""
    fecha: datetime
    moneda: str
    pago: str
    entrega: str
    igv: Optional[Decimal] = None
    total: Optional[Decimal] = None


@dataclass
class DatosProveedorExcel:
    """Datos del proveedor para generación de Excel directa."""
    razon_social: str
    nombre_contacto: str
    celular: Optional[str]
    correo: Optional[str]
    direccion: Optional[str]


@dataclass
class DatosProductoExcel:
    """Datos de producto para generación de Excel directa."""
    cantidad: int
    unidad_medida: str
    producto: str
    marca: Optional[str]
    modelo: Optional[str]
    precio_unitario: Decimal
    igv: str
