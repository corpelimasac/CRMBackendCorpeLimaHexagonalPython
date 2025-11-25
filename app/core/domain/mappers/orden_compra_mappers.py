"""
Mappers para transformar datos de órdenes de compra.

Estos mappers convierten entre DTOs de adaptadores y DTOs del dominio,
manteniendo la independencia del núcleo.
"""
from typing import Any, List
from decimal import Decimal
from datetime import datetime

from app.core.domain.dtos.orden_compra_dtos import (
    ObtenerInfoOCQuery,
    InfoOCProducto,
    InfoOCProveedor,
    InfoOCContacto,
    DetalleProductoOC,
    OrdenCompraCompleta,
    AuditoriaOrdenCompra,
    DatosExcelOC,
    DatosOrdenExcel,
    DatosProveedorExcel,
    DatosProductoExcel,
)


class OrdenCompraMapper:
    """
    Mapper para convertir entre diferentes representaciones de órdenes de compra.
    """

    @staticmethod
    def to_obtener_info_oc_query(
        id_usuario: int,
        id_cotizacion: int,
        id_version: int,
        id_contacto_proveedor: List[int],
        consorcio: bool
    ) -> ObtenerInfoOCQuery:
        """
        Crea un query del dominio desde parámetros individuales.

        Args:
            id_usuario: ID del usuario
            id_cotizacion: ID de la cotización
            id_version: ID de la versión de cotización
            id_contacto_proveedor: Lista de IDs de contactos de proveedor
            consorcio: Si es consorcio o no

        Returns:
            ObtenerInfoOCQuery: Query del dominio
        """
        return ObtenerInfoOCQuery(
            id_usuario=id_usuario,
            id_cotizacion=id_cotizacion,
            id_version=id_version,
            id_contacto_proveedor=id_contacto_proveedor,
            consorcio=consorcio
        )

    @staticmethod
    def from_db_row_to_info_producto(row: Any) -> InfoOCProducto:
        """
        Convierte una fila de base de datos a InfoOCProducto.

        Args:
            row: Fila de resultado de consulta SQL

        Returns:
            InfoOCProducto: DTO del dominio con información del producto
        """
        return InfoOCProducto(
            id_producto=row.id_producto,
            nombre_producto=row.nombre_producto,
            descripcion=getattr(row, 'descripcion', None),
            cantidad=row.cantidad,
            precio_unitario=Decimal(str(row.precio_unitario)),
            precio_total=Decimal(str(row.precio_total)),
            igv=row.igv if hasattr(row, 'igv') else 'CON IGV',
            id_producto_cotizacion=row.id_producto_cotizacion,
            marca=getattr(row, 'marca', None),
            unidad_medida=getattr(row, 'unidad_medida', None),
            modelo=getattr(row, 'modelo', None),
        )

    @staticmethod
    def from_db_row_to_info_proveedor(row: Any) -> InfoOCProveedor:
        """
        Convierte una fila de base de datos a InfoOCProveedor.

        Args:
            row: Fila de resultado de consulta SQL

        Returns:
            InfoOCProveedor: DTO del dominio con información del proveedor
        """
        return InfoOCProveedor(
            id_proveedor=row.id_proveedor,
            razon_social=row.razon_social,
            ruc=row.ruc,
            direccion=getattr(row, 'direccion', None),
            telefono=getattr(row, 'telefono', None),
            email=getattr(row, 'email', None),
        )

    @staticmethod
    def from_db_row_to_info_contacto(row: Any) -> InfoOCContacto:
        """
        Convierte una fila de base de datos a InfoOCContacto.

        Args:
            row: Fila de resultado de consulta SQL

        Returns:
            InfoOCContacto: DTO del dominio con información del contacto
        """
        return InfoOCContacto(
            id_contacto=row.id_contacto,
            nombre_completo=row.nombre_contacto,
            telefono=getattr(row, 'telefono_contacto', None),
            celular=getattr(row, 'celular_contacto', None),
            email=getattr(row, 'email_contacto', None),
        )

    @staticmethod
    def from_db_row_to_detalle_producto(row: Any) -> DetalleProductoOC:
        """
        Convierte una fila de base de datos a DetalleProductoOC.

        Args:
            row: Fila de resultado de consulta SQL

        Returns:
            DetalleProductoOC: DTO del dominio con detalle del producto
        """
        return DetalleProductoOC(
            id_oc_detalle=row.id_oc_detalle,
            id_orden=row.id_orden,
            id_producto=row.id_producto,
            nombre_producto=row.nombre_producto,
            cantidad=row.cantidad,
            precio_unitario=Decimal(str(row.precio_unitario)),
            precio_total=Decimal(str(row.precio_total)),
            igv=row.igv if hasattr(row, 'igv') else 'CON IGV',
            id_producto_cotizacion=getattr(row, 'id_producto_cotizacion', None),
            marca=getattr(row, 'marca', None),
            unidad_medida=getattr(row, 'unidad_medida', None),
            modelo=getattr(row, 'modelo', None),
        )

    @staticmethod
    def from_db_to_orden_completa(
        orden_data: Any,
        proveedor_data: Any,
        contacto_data: Any,
        productos_data: List[Any]
    ) -> OrdenCompraCompleta:
        """
        Convierte datos de base de datos a OrdenCompraCompleta.

        Args:
            orden_data: Datos de la orden
            proveedor_data: Datos del proveedor
            contacto_data: Datos del contacto
            productos_data: Lista de productos

        Returns:
            OrdenCompraCompleta: DTO del dominio con toda la información
        """
        proveedor = OrdenCompraMapper.from_db_row_to_info_proveedor(proveedor_data)
        contacto = OrdenCompraMapper.from_db_row_to_info_contacto(contacto_data)
        productos = [
            OrdenCompraMapper.from_db_row_to_detalle_producto(prod)
            for prod in productos_data
        ]

        return OrdenCompraCompleta(
            id_orden=orden_data.id_orden,
            numero_oc=orden_data.numero_oc,
            fecha_creacion=orden_data.fecha_creacion,
            moneda=orden_data.moneda,
            pago=orden_data.pago,
            entrega=orden_data.entrega,
            igv=Decimal(str(orden_data.igv)),
            total=Decimal(str(orden_data.total)),
            ruta_s3=getattr(orden_data, 'ruta_s3', None),
            consorcio=getattr(orden_data, 'consorcio', False),
            proveedor=proveedor,
            contacto=contacto,
            productos=productos,
            id_cotizacion=orden_data.id_cotizacion,
            id_cotizacion_versiones=orden_data.id_cotizacion_versiones,
            id_usuario=orden_data.id_usuario,
        )

    @staticmethod
    def from_db_to_auditoria(row: Any) -> AuditoriaOrdenCompra:
        """
        Convierte una fila de base de datos a AuditoriaOrdenCompra.

        Args:
            row: Fila de resultado de consulta SQL

        Returns:
            AuditoriaOrdenCompra: DTO del dominio con información de auditoría
        """
        return AuditoriaOrdenCompra(
            id_auditoria=row.id_auditoria,
            id_orden_compra=row.id_orden_compra,
            tipo_cambio=row.tipo_cambio,
            descripcion=row.descripcion,
            usuario=row.usuario,
            fecha=row.fecha if isinstance(row.fecha, datetime) else datetime.fromisoformat(str(row.fecha)),
            datos_anteriores=getattr(row, 'datos_anteriores', None),
            datos_nuevos=getattr(row, 'datos_nuevos', None),
        )

    @staticmethod
    def from_db_row_to_datos_excel(row: Any) -> DatosExcelOC:
        """
        Convierte una fila de base de datos a DatosExcelOC.

        Args:
            row: Fila de resultado de consulta SQL con todos los campos para Excel

        Returns:
            DatosExcelOC: DTO del dominio con datos para generar Excel
        """
        return DatosExcelOC(
            numero_oc=row.NUMERO_OC,
            id_cotizacion=row.IDCOTIZACION,
            id_version=row.IDVERSION,
            id_proveedor=row.IDPROVEEDOR,
            id_proveedor_contacto=row.IDPROVEEDORCONTACTO,
            cantidad=row.CANT,
            unidad_medida=row.UMED,
            producto=row.PRODUCTO,
            marca=getattr(row, 'MARCA', None),
            modelo=getattr(row, 'MODELO', None),
            precio_unitario=Decimal(str(row.PUNIT)),
            igv=row.IGV if hasattr(row, 'IGV') else 'CON IGV',
            precio_total=Decimal(str(row.TOTAL)),
            proveedor=row.PROVEEDOR,
            direccion=getattr(row, 'DIRECCION', None),
            personal=getattr(row, 'PERSONAL', None),
            telefono=getattr(row, 'TELEFONO', None),
            celular=getattr(row, 'CELULAR', None),
            correo=getattr(row, 'CORREO', None),
            fecha=row.FECHA if isinstance(row.FECHA, datetime) else datetime.fromisoformat(str(row.FECHA)),
            moneda=row.MONEDA,
            pago=row.PAGO,
        )

    @staticmethod
    def from_dict_to_datos_producto_excel(data: dict) -> DatosProductoExcel:
        """
        Convierte un diccionario a DatosProductoExcel.

        Args:
            data: Diccionario con datos del producto

        Returns:
            DatosProductoExcel: DTO del dominio
        """
        return DatosProductoExcel(
            cantidad=data.get('cantidad', 0),
            unidad_medida=data.get('unidadMedida', ''),
            producto=data.get('producto', ''),
            marca=data.get('marca'),
            modelo=data.get('modelo'),
            precio_unitario=Decimal(str(data.get('precioUnitario', 0))),
            igv=data.get('igv', 'CON IGV'),
        )

    @staticmethod
    def from_dict_to_datos_orden_excel(data: dict) -> DatosOrdenExcel:
        """
        Convierte un diccionario a DatosOrdenExcel.

        Args:
            data: Diccionario con datos de la orden

        Returns:
            DatosOrdenExcel: DTO del dominio
        """
        fecha = data.get('fecha')
        if isinstance(fecha, str):
            fecha = datetime.fromisoformat(fecha)
        elif not isinstance(fecha, datetime):
            fecha = datetime.now()

        return DatosOrdenExcel(
            fecha=fecha,
            moneda=data.get('moneda', 'SOLES'),
            pago=data.get('pago', ''),
            entrega=data.get('entrega', ''),
        )

    @staticmethod
    def from_dict_to_datos_proveedor_excel(data: dict) -> DatosProveedorExcel:
        """
        Convierte un diccionario a DatosProveedorExcel.

        Args:
            data: Diccionario con datos del proveedor

        Returns:
            DatosProveedorExcel: DTO del dominio
        """
        return DatosProveedorExcel(
            razon_social=data.get('razonSocial', 'Proveedor'),
            nombre_contacto=data.get('nombreContacto', ''),
            celular=data.get('celular'),
            correo=data.get('correo'),
            direccion=data.get('direccion'),
        )
