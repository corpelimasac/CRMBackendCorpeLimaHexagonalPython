"""
Excepciones específicas del dominio de Órdenes de Compra.

Estas excepciones son independientes de cualquier framework y representan
errores de negocio o validaciones del dominio.
"""
from typing import List, Optional


class OrdenCompraError(Exception):
    """Excepción base para errores relacionados con órdenes de compra."""

    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class OrdenCompraNotFoundError(OrdenCompraError):
    """Se lanza cuando no se encuentra una orden de compra."""

    def __init__(self, id_orden: int):
        self.id_orden = id_orden
        super().__init__(
            f"No se encontró la orden de compra con ID: {id_orden}",
            {"id_orden": id_orden}
        )


class ProductosSinRelacionError(OrdenCompraError):
    """
    Se lanza cuando productos no tienen id_producto_cotizacion.

    Este campo es obligatorio para relacionar los productos con la cotización.
    """

    def __init__(self, productos_sin_id: List[int]):
        self.productos_sin_id = productos_sin_id
        super().__init__(
            f"Los siguientes productos no tienen id_producto_cotizacion: {productos_sin_id}. "
            f"Este campo es obligatorio para relacionar los productos con la cotización.",
            {"productos_sin_id": productos_sin_id}
        )


class VersionCotizacionNotFoundError(OrdenCompraError):
    """Se lanza cuando la versión de cotización no existe."""

    def __init__(self, id_version: int):
        self.id_version = id_version
        super().__init__(
            f"La versión de cotización {id_version} no existe.",
            {"id_version": id_version}
        )


class DatosInsuficientesError(OrdenCompraError):
    """Se lanza cuando no hay datos suficientes para generar una orden."""

    def __init__(self, mensaje: str = "No se encontraron datos para los parámetros especificados"):
        super().__init__(mensaje)


class GeneracionExcelError(OrdenCompraError):
    """Se lanza cuando hay un error al generar archivos Excel."""

    def __init__(self, detalle: str, id_contacto: Optional[int] = None):
        self.id_contacto = id_contacto
        mensaje = f"Error al generar Excel: {detalle}"
        if id_contacto:
            mensaje = f"Error al generar Excel para contacto {id_contacto}: {detalle}"
        super().__init__(mensaje, {"detalle": detalle, "id_contacto": id_contacto})


class AlmacenamientoError(OrdenCompraError):
    """Se lanza cuando hay un error al almacenar archivos."""

    def __init__(self, detalle: str, filename: Optional[str] = None):
        self.filename = filename
        mensaje = f"Error al almacenar archivo: {detalle}"
        if filename:
            mensaje = f"Error al almacenar archivo '{filename}': {detalle}"
        super().__init__(mensaje, {"detalle": detalle, "filename": filename})


class ActualizacionOrdenError(OrdenCompraError):
    """Se lanza cuando hay un error al actualizar una orden."""

    def __init__(self, id_orden: int, detalle: str):
        self.id_orden = id_orden
        super().__init__(
            f"Error al actualizar orden {id_orden}: {detalle}",
            {"id_orden": id_orden, "detalle": detalle}
        )


class EliminacionOrdenError(OrdenCompraError):
    """Se lanza cuando hay un error al eliminar una orden."""

    def __init__(self, id_orden: int, detalle: str):
        self.id_orden = id_orden
        super().__init__(
            f"Error al eliminar orden {id_orden}: {detalle}",
            {"id_orden": id_orden, "detalle": detalle}
        )
