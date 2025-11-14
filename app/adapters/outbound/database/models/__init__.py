"""
Modelos de base de datos SQLAlchemy
"""
from .base import Base

# Modelos principales
from .usuarios_model import UsuariosModel
from .trabajadores_model import TrabajadoresModel
from .cotizacion_model import CotizacionModel

# Modelos de registro de compras (antes de ordenes_compra por FK)
from .registro_compra_model import RegistroCompraModel
from .registro_compra_orden_model import RegistroCompraOrdenModel
from .registro_compra_auditoria_model import RegistroCompraAuditoriaModel
from .tasa_cambio_sunat_model import TasaCambioSunatModel

from .ordenes_compra_model import OrdenesCompraModel
from .ordenes_compra_auditoria_model import OrdenesCompraAuditoriaModel



# Modelos de proveedores
from .proveedores_model import ProveedoresModel
from .proveedor_contacto_model import ProveedorContactosModel
from .proveedor_detalle_model import ProveedorDetalleModel
from .intermedia_proveedor_contacto_model import intermedia_proveedor_contacto

# Modelos de productos
from .productos_model import ProductosModel
from .categoria import CategoriaModel
from .subcategoria_model import SubcategoriaModel
from .elemento_especifico_model import ElementoEspecificoModel
from .marcas_model import MarcasModel
from .unidad_medida_model import UnidadMedidaModel

# Modelos de cotizaciones
from .cotizaciones_versiones_model import CotizacionesVersionesModel
from .productos_cotizaciones_model import ProductosCotizacionesModel

# Modelos de descuentos
from .producto_descuento_model import ProductoDescuentoModel
from .producto_descuento_admin_model import ProductoDescuentoAdminModel
from .descuento_vendedor_modal import DescuentoVendedorModel

# Modelos de utilidad
from .porcentaje_utilidad_model import PorcentajeUtilidadModel

__all__ = [
    "Base",
    "UsuariosModel",
    "TrabajadoresModel",
    "CotizacionModel",
    "RegistroCompraModel",
    "RegistroCompraOrdenModel",
    "RegistroCompraAuditoriaModel",
    "TasaCambioSunatModel",
    "OrdenesCompraModel",
    "OrdenesCompraAuditoriaModel",
    "ProveedoresModel",
    "ProveedorContactosModel",
    "ProveedorDetalleModel",
    "intermedia_proveedor_contacto",
    "ProductosModel",
    "CategoriaModel",
    "SubcategoriaModel",
    "ElementoEspecificoModel",
    "MarcasModel",
    "UnidadMedidaModel",
    "CotizacionesVersionesModel",
    "ProductosCotizacionesModel",
    "ProductoDescuentoModel",
    "ProductoDescuentoAdminModel",
    "DescuentoVendedorModel",
    "PorcentajeUtilidadModel"
] 