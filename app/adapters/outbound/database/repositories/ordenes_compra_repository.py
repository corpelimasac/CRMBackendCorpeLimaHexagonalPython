"""
Repositorio para órdenes de compra
"""
from sqlalchemy.orm import Session
from sqlalchemy import text, case   
from typing import Optional, List, Any
from app.adapters.outbound.database.models.ordenes_compra_model import OrdenesCompraModel
from app.adapters.outbound.database.models.cotizaciones_versiones_model import CotizacionesVersionesModel
from app.adapters.outbound.database.models.productos_cotizaciones_model import ProductosCotizacionesModel
from app.adapters.outbound.database.models.productos_model import ProductosModel
from app.adapters.outbound.database.models.unidad_medida_model import UnidadMedidaModel
from app.adapters.outbound.database.models.marcas_model import MarcasModel
from app.adapters.outbound.database.models.proveedores_model import ProveedoresModel
from app.adapters.outbound.database.models.proveedor_contacto_model import ProveedorContactosModel
from app.adapters.outbound.database.models.proveedor_detalle_model import ProveedorDetalleModel
from app.adapters.outbound.database.models.intermedia_proveedor_contacto_model import intermedia_proveedor_contacto
from app.adapters.inbound.api.schemas.generar_oc_schemas import GenerarOCRequest

class OrdenesCompraRepository:
    """
    Repositorio para manejar las operaciones de base de datos relacionadas con órdenes de compra
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def crear_orden_compra(self, datos_oc: dict) -> Optional[OrdenesCompraModel]:
        """
        Crea una nueva orden de compra en la base de datos
        
        Args:
            datos_oc (dict): Datos de la orden de compra
            
        Returns:
            OrdenesCompraModel: La orden de compra creada o None si hay error
        """
        try:
            # Crear la nueva orden de compra sin correlativo primero
            nueva_oc = OrdenesCompraModel(
                correlative="TEMP",  # Correlativo temporal
                id_cotizacion=datos_oc.get('id_cotizacion'),
                id_usuario=datos_oc.get('id_usuario'),
                ruta_s3=datos_oc.get('ruta_s3'),
                version=datos_oc.get('version'),
                activo=True,
                moneda=datos_oc.get('moneda'),
                igv=datos_oc.get('igv'),
                total=datos_oc.get('total'),
                id_proveedor=datos_oc.get('id_proveedor')
            )
            
            self.db.add(nueva_oc)
            self.db.commit()
            self.db.refresh(nueva_oc)
            
            # Generar el correlativo basado en el id_orden auto-generado
            #year = nueva_oc.fecha_creacion.year if nueva_oc.fecha_creacion else 2025
            numero_correlativo = f"OC-{nueva_oc.id_orden:05d}"
            
            # Actualizar la orden con el correlativo correcto
            nueva_oc.correlative = numero_correlativo
            self.db.commit()
            self.db.refresh(nueva_oc)
            
            return nueva_oc
            
        except Exception as e:
            self.db.rollback()
            print(f"Error al crear orden de compra: {e}")
            return None
    
    def obtener_orden_por_id(self, id_orden: int) -> Optional[OrdenesCompraModel]:
        """
        Obtiene una orden de compra por su ID
        
        Args:
            id_orden (int): ID de la orden de compra
            
        Returns:
            OrdenesCompraModel: La orden de compra encontrada o None
        """
        return self.db.query(OrdenesCompraModel).filter(
            OrdenesCompraModel.id_orden == id_orden
        ).first()
    
    def obtener_orden_por_codigo(self, cod_oc: str) -> Optional[OrdenesCompraModel]:
        """
        Obtiene una orden de compra por su código
        
        Args:
            cod_oc (str): Código de la orden de compra (ej: "OC-0001")
            
        Returns:
            OrdenesCompraModel: La orden de compra encontrada o None
        """
        return self.db.query(OrdenesCompraModel).filter(
            OrdenesCompraModel.correlative == cod_oc
        ).first()
    
    def listar_ordenes_por_cotizacion(self, id_cotizacion: int) -> list[OrdenesCompraModel]:
        """
        Lista todas las órdenes de compra de una cotización específica
        
        Args:
            id_cotizacion (int): ID de la cotización
            
        Returns:
            list[OrdenesCompraModel]: Lista de órdenes de compra
        """
        return self.db.query(OrdenesCompraModel).filter(
            OrdenesCompraModel.id_cotizacion == id_cotizacion,
            OrdenesCompraModel.activo == True
        ).all() 
    

    def obtener_info_oc(self, request: GenerarOCRequest) -> List[Any]:
        """
        Obtiene información de productos para generar orden de compra
        
        Args:
            request (GenerarOCRequest): Datos de la solicitud
            
        Returns:
            List[Any]: Lista de resultados de la consulta
        """
        try:
            print(f"Ejecutando consulta para cotización: {request.id_cotizacion}, versión: {request.id_version}")
            print(f"Contactos de proveedor: {request.id_contacto_proveedor}")
            
            query = self.db.query(
                CotizacionesVersionesModel.id_cotizacion.label('IDCOTIZACION'),
                CotizacionesVersionesModel.id_cotizacion_versiones.label('IDVERSION'),
                ProductosCotizacionesModel.cantidad.label('CANT'),
                UnidadMedidaModel.descripcion.label('UMED'),
                ProductosModel.nombre.label('PRODUCTO'),
                MarcasModel.nombre.label('MARCA'),
                ProductosModel.modelo_marca.label('MODELO'),
                CotizacionesVersionesModel.fecha_modificacion.label('FECHA'),
                ProveedoresModel.id_proveedor.label('IDPROVEEDOR'),
                ProveedoresModel.razon_social.label('PROVEEDOR'),
                ProveedorContactosModel.id_proveedor_contacto.label('IDPROVEEDORCONTACTO'),
                ProveedorContactosModel.nombre.label('PERSONAL'),
                ProveedorContactosModel.telefono.label('TELEFONO'),
                ProveedorContactosModel.celular.label('CELULAR'),
                ProveedorContactosModel.correo.label('CORREO'),
                ProveedoresModel.direccion.label('DIRECCION'),
                case(
                    (ProveedorDetalleModel.moneda == 'S/.', 'SOLES'),
                    else_='DOLARES'
                ).label('MONEDA'),
                ProveedoresModel.condiciones_pago.label('PAGO'),
                ProveedorDetalleModel.precio_costo_unitario.label('PUNIT'),
                ProveedorDetalleModel.igv.label('IGV'),
                (ProductosCotizacionesModel.cantidad * ProveedorDetalleModel.precio_costo_unitario).label('TOTAL')
            ).select_from(CotizacionesVersionesModel)\
             .join(ProductosCotizacionesModel, CotizacionesVersionesModel.id_cotizacion_versiones == ProductosCotizacionesModel.id_cotizacion_versiones)\
             .join(ProductosModel, ProductosCotizacionesModel.id_producto == ProductosModel.id_producto)\
             .join(UnidadMedidaModel, ProductosModel.id_unidad_medida == UnidadMedidaModel.id_unidad_medida)\
             .join(MarcasModel, ProductosModel.id_marca == MarcasModel.id_marca)\
             .join(ProveedoresModel, ProductosModel.id_proveedor == ProveedoresModel.id_proveedor)\
             .join(intermedia_proveedor_contacto, ProveedoresModel.id_proveedor == intermedia_proveedor_contacto.c.id_proveedor)\
             .join(ProveedorContactosModel, intermedia_proveedor_contacto.c.id_proveedor_contacto == ProveedorContactosModel.id_proveedor_contacto)\
             .join(ProveedorDetalleModel, ProductosModel.id_producto == ProveedorDetalleModel.id_producto)\
             .filter(CotizacionesVersionesModel.id_cotizacion == request.id_cotizacion)\
             .filter(ProductosCotizacionesModel.id_cotizacion_versiones == request.id_version)\
             .filter(ProveedorContactosModel.id_proveedor_contacto.in_(request.id_contacto_proveedor))
            
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