"""
Mappers para transformar datos de productos de cotización.

Estos mappers convierten entre representaciones de base de datos y DTOs del dominio.
"""
from typing import Any
from decimal import Decimal

from app.core.domain.dtos.producto_cotizacion_dtos import (
    ProductoCotizacionDisponible,
    ProductoCotizacionInfo,
)


class ProductoCotizacionMapper:
    """
    Mapper para convertir entre diferentes representaciones de productos de cotización.
    """

    @staticmethod
    def from_db_row_to_disponible(row: Any) -> ProductoCotizacionDisponible:
        """
        Convierte una fila de base de datos a ProductoCotizacionDisponible.

        Args:
            row: Fila de resultado de consulta SQL con campos específicos

        Returns:
            ProductoCotizacionDisponible: DTO del dominio con información del producto
        """
        return ProductoCotizacionDisponible(
            # IDs de relación
            id_producto_cotizacion=row.IDPRODUCTOCOTIZACION,
            id_proveedor=row.IDPROVEEDOR,
            id_producto=row.IDPRODUCTO,

            # Datos del proveedor
            razon_social=row.RAZONSOCIAL,
            direccion=row.DIRECCION if hasattr(row, 'DIRECCION') else None,
            entrega=row.ENTREGA if hasattr(row, 'ENTREGA') else None,
            pago=row.PAGO if hasattr(row, 'PAGO') else None,
            moneda=row.MONEDA,

            # Datos del producto
            cantidad=row.CANT,
            unidad_medida=row.UMED,
            producto=row.PRODUCTO,
            marca=row.MARCA if hasattr(row, 'MARCA') else None,
            modelo=row.MODELO if hasattr(row, 'MODELO') else None,

            # Precios
            precio_unitario=Decimal(str(row.PUNIT)),
            igv=row.IGV if hasattr(row, 'IGV') else 'CON IGV',
            precio_total=Decimal(str(row.PTOTAL)),
        )

    @staticmethod
    def from_db_row_to_info(row: Any) -> ProductoCotizacionInfo:
        """
        Convierte una fila de base de datos a ProductoCotizacionInfo.

        Args:
            row: Fila de resultado de consulta SQL

        Returns:
            ProductoCotizacionInfo: DTO del dominio con información básica
        """
        return ProductoCotizacionInfo(
            id_producto_cotizacion=row.id_producto_cotizacion,
            id_producto=row.id_producto,
            nombre_producto=row.nombre_producto if hasattr(row, 'nombre_producto') else str(row.id_producto),
            cantidad=row.cantidad,
            precio_unitario=Decimal(str(row.precio_unitario)),
            precio_total=Decimal(str(row.precio_total)),
            igv=row.igv if hasattr(row, 'igv') else 'CON IGV',
            marca=getattr(row, 'marca', None),
            modelo=getattr(row, 'modelo', None),
            unidad_medida=getattr(row, 'unidad_medida', None),
        )
