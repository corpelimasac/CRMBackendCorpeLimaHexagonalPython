from sqlalchemy.orm import Session
from sqlalchemy import case, select, Row
from typing import List, Any, Sequence
import logging

from app.adapters.outbound.database.models.productos_cotizaciones_model import ProductosCotizacionesModel
from app.adapters.outbound.database.models.proveedores_model import ProveedoresModel
from app.adapters.outbound.database.models.proveedor_detalle_model import ProveedorDetalleModel
from app.adapters.outbound.database.models.unidad_medida_model import UnidadMedidaModel
from app.adapters.outbound.database.models.productos_model import ProductosModel
from app.adapters.outbound.database.models.marcas_model import MarcasModel
from app.adapters.outbound.database.models.cotizaciones_versiones_model import CotizacionesVersionesModel
from app.core.ports.repositories.productos_cotizaciones_repository import ProductosCotizacionesRepositoryPort

logger = logging.getLogger(__name__)

class ProductosCotizacionesRepository(ProductosCotizacionesRepositoryPort):
    """
    Repositorio para manejar las operaciones de base de datos relacionadas con los productos de las cotizaciones
    """

    def __init__(self, db: Session):
        self.db = db

    def obtener_productos_cotizaciones(self, id_cotizacion: int, id_cotizacion_version: int) -> Sequence[Row[
        tuple[Any, ...] | Any]] | list[Any]:
        """
        Obtiene la informacion de los productos de la cotizacion

        Args:
            id_cotizacion (int): ID de la cotización
            id_cotizacion_version (int): ID de la versión de la cotización

        Returns:
            List[Any]: Lista de resultados de la consulta
        """
        try:
            logger.info(f"Obteniendo productos para cotización: {id_cotizacion}, versión: {id_cotizacion_version}")

            stmt = (
                select(
                    ProveedoresModel.id_proveedor.label('IDPROVEEDOR'),
                    ProveedoresModel.razon_social.label('RAZONSOCIAL'),
                    ProveedoresModel.direccion.label('DIRECCION'),
                    ProveedoresModel.forma_entrega.label('ENTREGA'),
                    ProveedoresModel.condiciones_pago.label('PAGO'),
                    case(
                        (ProveedorDetalleModel.moneda == 'S/.', 'SOLES'),
                        else_='DOLARES'
                    ).label('MONEDA'),
                    ProductosCotizacionesModel.cantidad.label('CANT'),
                    UnidadMedidaModel.descripcion.label('UMED'),
                    ProductosModel.id_producto.label('IDPRODUCTO'),
                    ProductosModel.nombre.label('PRODUCTO'),
                    MarcasModel.nombre.label('MARCA'),
                    ProductosModel.modelo_marca.label('MODELO'),
                    ProveedorDetalleModel.precio_costo_unitario.label('PUNIT'),
                    ProveedorDetalleModel.igv.label('IGV'),
                    (ProductosCotizacionesModel.cantidad * ProveedorDetalleModel.precio_costo_unitario).label('PTOTAL')
                )
                .select_from(ProductosCotizacionesModel)
                .join(CotizacionesVersionesModel,
                      ProductosCotizacionesModel.id_cotizacion_versiones == CotizacionesVersionesModel.id_cotizacion_versiones)
                .join(ProductosModel,
                      ProductosCotizacionesModel.id_producto == ProductosModel.id_producto)
                .join(UnidadMedidaModel,
                      ProductosModel.id_unidad_medida == UnidadMedidaModel.id_unidad_medida)
                .outerjoin(MarcasModel,
                           ProductosModel.id_marca == MarcasModel.id_marca)
                .join(ProveedorDetalleModel,
                      ProductosModel.id_producto == ProveedorDetalleModel.id_producto)
                .join(ProveedoresModel,
                      ProductosModel.id_proveedor == ProveedoresModel.id_proveedor)
                .where(CotizacionesVersionesModel.id_cotizacion == id_cotizacion)
                .where(CotizacionesVersionesModel.id_cotizacion_versiones == id_cotizacion_version)
            )

            result = self.db.execute(stmt).all()
            logger.info(f"Se obtuvieron {len(result)} productos")
            return result
        except Exception as e:
            logger.error(f"Error al obtener productos de la cotización: {e}")
            return []