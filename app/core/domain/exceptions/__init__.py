"""
Excepciones del dominio.

Este módulo contiene todas las excepciones específicas del dominio,
independientes de cualquier framework o infraestructura.
"""

from .orden_compra_exceptions import (
    OrdenCompraError,
    OrdenCompraNotFoundError,
    ProductosSinRelacionError,
    VersionCotizacionNotFoundError,
    DatosInsuficientesError,
    GeneracionExcelError,
    AlmacenamientoError,
    ActualizacionOrdenError,
    EliminacionOrdenError,
)

__all__ = [
    "OrdenCompraError",
    "OrdenCompraNotFoundError",
    "ProductosSinRelacionError",
    "VersionCotizacionNotFoundError",
    "DatosInsuficientesError",
    "GeneracionExcelError",
    "AlmacenamientoError",
    "ActualizacionOrdenError",
    "EliminacionOrdenError",
]
