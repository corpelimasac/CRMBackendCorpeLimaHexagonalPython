from app.core.ports.repositories.ordenes_compra_repository import OrdenesCompraRepositoryPort
from app.core.domain.entities.ordenes_compra import OrdenesCompra
from sqlalchemy.orm import Session
from app.adapters.outbound.database.models.ordenes_compra_model import OrdenesCompraModel
from app.adapters.outbound.database.models.ordenes_compra_detalles_model import OrdenesCompraDetallesModel
from datetime import datetime
from app.adapters.inbound.api.schemas.generar_oc_schemas import GenerarOCRequest
from typing import List, Any
from sqlalchemy import case, func
from app.adapters.outbound.database.models.cotizaciones_versiones_model import CotizacionesVersionesModel
from app.adapters.outbound.database.models.productos_cotizaciones_model import ProductosCotizacionesModel
from app.adapters.outbound.database.models.unidad_medida_model import UnidadMedidaModel
from app.adapters.outbound.database.models.marcas_model import MarcasModel
from app.adapters.outbound.database.models.proveedores_model import ProveedoresModel
from app.adapters.outbound.database.models.proveedor_detalle_model import ProveedorDetalleModel
from app.adapters.outbound.database.models.productos_model import ProductosModel
from app.adapters.outbound.database.models.intermedia_proveedor_contacto_model import intermedia_proveedor_contacto
from app.adapters.outbound.database.models.proveedor_contacto_model import ProveedorContactosModel
from app.adapters.outbound.database.models.ordenes_compra_model import OrdenesCompraModel


class OrdenesCompraRepository(OrdenesCompraRepositoryPort):

    def __init__(self, db: Session):
        self.db = db

    def save(self, order: OrdenesCompra) -> OrdenesCompra:
        try:
            # 1. Obtener el último correlativo
           
            last_correlative = self.db.query(OrdenesCompraModel).order_by(OrdenesCompraModel.id_orden.desc()).first()
            if last_correlative:
                last_number = int(last_correlative.correlative.split('-')[1])
                new_number = last_number + 1
            else:
                new_number = 1

            current_year = datetime.now().year
            # 2. Generar el correlativo
            new_correlative = f"OC-{new_number:06d}-{current_year}"
            print(f"Este es el correlativo: {new_correlative}")
            db_order = OrdenesCompraModel(
                id_cotizacion=order.id_cotizacion,
                id_proveedor=order.id_proveedor,
                id_proveedor_contacto=order.id_proveedor_contacto,
                moneda=order.moneda,
                pago=order.pago,
                entrega=order.entrega,
                id_cotizacion_versiones=order.id_cotizacion_versiones,
                fecha_creacion=datetime.now(),
                correlative=new_correlative, 
                id_usuario=order.id_usuario
            )

            # --- 2. Insertar la Orden Principal ---
            self.db.add(db_order)
            # Hacemos un "flush" para que la base de datos asigne el ID autoincremental
            # sin hacer un commit completo de la transacción.
            self.db.flush() 

            # --- 3. Mapeo e Inserción de los Detalles ---
            for item in order.items:
                db_detail = OrdenesCompraDetallesModel(
                    id_orden=db_order.id_orden, # <-- Usamos el ID recién generado
                    id_producto=item.id_producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.p_unitario,
                    precio_total=item.p_total
                )
                self.db.add(db_detail)

            # --- 4. Confirmar la Transacción ---
            self.db.commit()
            
            # (Opcional) Refrescar el objeto para tener todos los datos de la DB
            #self.db.refresh(db_order) 
            
            return order

        except Exception as e:
            # Si algo falla, revertimos todos los cambios de esta transacción
            self.db.rollback()
            print(f"Error al guardar la orden de compra: {e}")
            raise e # Vuelve a lanzar la excepción para que el caso de uso la maneje
        

    def obtener_info_oc(self, request: GenerarOCRequest) -> List[Any]:
        
        """
        Obtiene información de productos para generar orden de compra desde las tablas de órdenes ya guardadas
        
        Args:
            request (GenerarOCRequest): Datos de la solicitud
            
        Returns:
            List[Any]: Lista de resultados de la consulta
        """
        try:
            print(f"Ejecutando consulta para cotización: {request.id_cotizacion}, versión: {request.id_version}")
            print(f"Contactos de proveedor: {request.id_contacto_proveedor}")

            latest_order_id_subquery = self.db.query(
                OrdenesCompraModel.id_orden
            ).filter(
                OrdenesCompraModel.id_cotizacion == request.id_cotizacion,
                OrdenesCompraModel.id_cotizacion_versiones == request.id_version,
                OrdenesCompraModel.id_proveedor_contacto.in_(request.id_contacto_proveedor)
            ).order_by(
            OrdenesCompraModel.id_orden.desc()  # Ordenamos por ID descendente para obtener el último
            ).limit(
            1
            ).scalar_subquery()
            
            query = self.db.query(
                OrdenesCompraModel.correlative.label('NUMERO_OC'),
                OrdenesCompraModel.id_cotizacion.label('IDCOTIZACION'),
                OrdenesCompraModel.id_cotizacion_versiones.label('IDVERSION'),
                OrdenesCompraDetallesModel.cantidad.label('CANT'),
                UnidadMedidaModel.descripcion.label('UMED'),
                ProductosModel.nombre.label('PRODUCTO'),
                MarcasModel.nombre.label('MARCA'),
                ProductosModel.modelo_marca.label('MODELO'),
                func.date(OrdenesCompraModel.fecha_creacion).label('FECHA'),
                ProveedoresModel.id_proveedor.label('IDPROVEEDOR'),
                ProveedoresModel.razon_social.label('PROVEEDOR'),
                OrdenesCompraModel.id_proveedor_contacto.label('IDPROVEEDORCONTACTO'),
                ProveedorContactosModel.nombre.label('PERSONAL'),
                ProveedorContactosModel.telefono.label('TELEFONO'),
                ProveedorContactosModel.celular.label('CELULAR'),
                ProveedorContactosModel.correo.label('CORREO'),
                ProveedoresModel.direccion.label('DIRECCION'),
                OrdenesCompraModel.moneda.label('MONEDA'),
                OrdenesCompraModel.pago.label('PAGO'),
                OrdenesCompraDetallesModel.precio_unitario.label('PUNIT'),
                case(
                    (ProveedorDetalleModel.igv=="SIN IGV", 'SIN IGV'),
                    else_=ProveedorDetalleModel.igv=="CON IGV"
                ).label('IGV'),
                OrdenesCompraDetallesModel.precio_total.label('TOTAL')
            ).select_from(OrdenesCompraModel)\
             .join(OrdenesCompraDetallesModel, OrdenesCompraModel.id_orden == OrdenesCompraDetallesModel.id_orden)\
             .join(ProductosModel, OrdenesCompraDetallesModel.id_producto == ProductosModel.id_producto)\
             .join(UnidadMedidaModel, ProductosModel.id_unidad_medida == UnidadMedidaModel.id_unidad_medida)\
             .join(MarcasModel, ProductosModel.id_marca == MarcasModel.id_marca)\
             .join(ProveedoresModel, OrdenesCompraModel.id_proveedor == ProveedoresModel.id_proveedor)\
             .join(ProveedorDetalleModel, ProductosModel.id_producto == ProveedorDetalleModel.id_producto)\
             .join(ProveedorContactosModel, OrdenesCompraModel.id_proveedor_contacto == ProveedorContactosModel.id_proveedor_contacto)\
             .filter(OrdenesCompraModel.id_orden == latest_order_id_subquery)
            
            resultados = query.all()
            print(f"Consulta ejecutada. Resultados obtenidos: {len(resultados)}")
            
            if resultados:
                print(f"Primer resultado: {resultados[0]}")
            
            return resultados
            
        except Exception as e:
            print(f"Error en obtener_info_oc: {e}")
            import traceback
            traceback.print_exc()
            return []

    def actualizar_ruta_s3(self, id_orden: int, ruta_s3: str) -> bool:
        """
        Actualiza la ruta S3 de una orden de compra específica
        
        Args:
            id_orden (int): ID de la orden de compra
            ruta_s3 (str): URL del archivo en S3
            
        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        try:
            orden = self.db.query(OrdenesCompraModel).filter(
                OrdenesCompraModel.id_orden == id_orden 
            ).first()
            print(f"Este es el orden: {orden}")
            
            if orden:
                orden.ruta_s3 = ruta_s3
                self.db.commit()
                print(f"URL S3 actualizada para orden {id_orden}: {ruta_s3}")
                return True
            else:
                print(f"No se encontró orden con ID {id_orden}")
                return False
                
        except Exception as e:
            print(f"Error al actualizar ruta S3: {e}")
            self.db.rollback()
            return False

    def obtener_ordenes_por_contacto_y_version(self, id_cotizacion: int, id_version: int, id_contacto: int) -> List[OrdenesCompraModel]:
        """
        Obtiene las órdenes de compra de un contacto específico en una versión de cotización
        
        Args:
            id_cotizacion (int): ID de la cotización
            id_version (int): ID de la versión
            id_contacto (int): ID del contacto del proveedor
            
        Returns:
            List[OrdenesCompraModel]: Lista de órdenes encontradas

        """
 
        try:
            query = self.db.query(OrdenesCompraModel).filter(
                OrdenesCompraModel.id_cotizacion == id_cotizacion,
                OrdenesCompraModel.id_cotizacion_versiones == id_version,
                OrdenesCompraModel.id_proveedor_contacto == id_contacto
            )

            query = query.order_by(OrdenesCompraModel.id_orden.desc())
            latest_order = query.first()

            if latest_order:
                return [latest_order]
            else:
                return []
            
        except Exception as e:
            print(f"Error al obtener órdenes por contacto: {e}")
            return []
 
 