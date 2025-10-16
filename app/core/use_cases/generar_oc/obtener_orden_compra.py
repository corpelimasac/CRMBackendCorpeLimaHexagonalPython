import logging
from fastapi import HTTPException
from app.core.ports.repositories.ordenes_compra_repository import OrdenesCompraRepositoryPort
from app.adapters.inbound.api.schemas.ordenes_compra_schemas import (
    OrdenCompraDetalleResponse,
    ProveedorOrdenResponse,
    ProductoOrdenResponse
)

logger = logging.getLogger(__name__)


class ObtenerOrdenCompra:
    """
    Caso de uso para obtener una orden de compra completa con todos sus datos.

    Este caso de uso:
    1. Obtiene la orden por ID
    2. Obtiene todos los datos del proveedor y contacto
    3. Obtiene todos los productos con sus detalles
    4. Formatea la respuesta en el DTO correspondiente

    Arquitectura Hexagonal:
    - Caso de uso en la capa de aplicación
    - Se comunica con el puerto del repositorio
    - Retorna un DTO para la capa de presentación
    """

    def __init__(self, ordenes_compra_repo: OrdenesCompraRepositoryPort):
        """
        Inicializa el caso de uso con las dependencias necesarias.

        Args:
            ordenes_compra_repo: Repositorio de órdenes de compra
        """
        self.ordenes_compra_repo = ordenes_compra_repo

    def execute(self, id_orden: int) -> OrdenCompraDetalleResponse:
        """
        Ejecuta el caso de uso de obtención de orden de compra.

        Args:
            id_orden (int): ID de la orden de compra a obtener

        Returns:
            OrdenCompraDetalleResponse: Datos completos de la orden

        Raises:
            HTTPException: Si hay errores durante el proceso
        """
        try:
            logger.info(f"Obteniendo orden de compra ID: {id_orden}")

            # Obtener datos completos de la orden
            resultados = self.ordenes_compra_repo.obtener_orden_completa(id_orden)

            if not resultados:
                raise HTTPException(
                    status_code=404,
                    detail=f"Orden de compra con ID {id_orden} no encontrada"
                )

            # El primer registro tiene los datos generales de la orden y proveedor
            primer_registro = resultados[0]

            # Construir datos del proveedor (son los mismos para todos los productos)
            proveedor_data = ProveedorOrdenResponse(
                idProveedor=primer_registro.IDPROVEEDOR,
                razonSocial=primer_registro.PROVEEDOR,
                direccion=primer_registro.DIRECCION or "",
                idProveedorContacto=primer_registro.IDPROVEEDORCONTACTO,
                nombreContacto=primer_registro.PERSONAL,
                telefono=str(primer_registro.TELEFONO) if primer_registro.TELEFONO else None,
                celular=str(primer_registro.CELULAR) if primer_registro.CELULAR else None,
                correo=primer_registro.CORREO
            )

            # Construir lista de productos
            productos_data = []
            for registro in resultados:
                producto = ProductoOrdenResponse(
                    idOcDetalle=registro.ID_OC_DETALLE,
                    idProducto=registro.IDPRODUCTO,
                    producto=registro.PRODUCTO,
                    marca=registro.MARCA,
                    modelo=registro.MODELO or "",
                    unidadMedida=registro.UMED,
                    cantidad=registro.CANT,
                    precioUnitario=float(registro.PUNIT),
                    precioTotal=float(registro.TOTAL),
                    igv=registro.IGV
                )
                productos_data.append(producto)

            # Construir respuesta completa
            orden_response = OrdenCompraDetalleResponse(
                idOrden=primer_registro.ID_ORDEN,
                numeroOc=primer_registro.NUMERO_OC,
                idCotizacion=primer_registro.IDCOTIZACION,
                idVersion=primer_registro.IDVERSION,
                fecha=str(primer_registro.FECHA),
                moneda=primer_registro.MONEDA,
                pago=primer_registro.PAGO,
                entrega=primer_registro.ENTREGA,
                total=float(primer_registro.TOTAL_ORDEN) if primer_registro.TOTAL_ORDEN else 0.0,
                rutaS3=primer_registro.RUTA_S3,
                proveedor=proveedor_data,
                productos=productos_data
            )

            logger.info(f"Orden {id_orden} obtenida exitosamente con {len(productos_data)} productos")
            return orden_response

        except ValueError as e:
            logger.error(f"Error de validación: {e}")
            raise HTTPException(status_code=404, detail=str(e))

        except HTTPException:
            raise

        except Exception as e:
            logger.error(f"Error al obtener orden de compra {id_orden}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error interno al obtener la orden de compra: {str(e)}"
            )
