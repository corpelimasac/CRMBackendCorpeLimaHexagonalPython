import logging
import math
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, or_, func
from app.adapters.outbound.database.models.ordenes_compra_auditoria_model import OrdenesCompraAuditoriaModel
from app.adapters.outbound.database.models.ordenes_compra_model import OrdenesCompraModel
from app.adapters.outbound.database.models.usuarios_model import UsuariosModel
from app.adapters.outbound.database.models.trabajadores_model import TrabajadoresModel
from app.adapters.outbound.database.models.proveedores_model import ProveedoresModel
from app.adapters.outbound.database.models.proveedor_contacto_model import ProveedorContactosModel
from app.adapters.outbound.database.models.productos_model import ProductosModel

logger = logging.getLogger(__name__)


def _parsear_cambio_concatenado(campo: Optional[str]) -> tuple:
    """
    Parsea un campo concatenado con formato 'id_anterior ----> id_nuevo' o solo 'id'

    Returns:
        tuple: (id_anterior o None, id_nuevo o None)
    """
    if not campo:
        return None, None

    if ' ----> ' in campo:
        partes = campo.split(' ----> ')
        try:
            return int(partes[0].strip()), int(partes[1].strip())
        except:
            return None, None
    else:
        try:
            return None, int(campo.strip())
        except:
            return None, None


class ListarAuditoriaOrdenCompra:
    """
    Caso de uso optimizado para listar auditorías de órdenes de compra.

    Este caso de uso:
    1. Hace JOINs para obtener datos relacionados (numero_oc, usuario, etc.)
    2. Parsea campos concatenados (cambio_proveedor, cambio_contacto, cambio_monto)
    3. Resuelve nombres de proveedores, contactos y productos mediante consultas
    4. Retorna datos en formato optimizado
    """

    def __init__(self, db: Session):
        self.db = db

    def _obtener_nombre_proveedor(self, id_proveedor: Optional[int]) -> str:
        """Obtiene el nombre del proveedor por su ID"""
        if not id_proveedor:
            return ""

        proveedor = self.db.query(ProveedoresModel).filter(
            ProveedoresModel.id_proveedor == id_proveedor
        ).first()

        return proveedor.razon_social if proveedor else f"ID:{id_proveedor}"

    def _obtener_nombre_contacto(self, id_contacto: Optional[int]) -> str:
        """Obtiene el nombre del contacto por su ID"""
        if not id_contacto:
            return ""

        contacto = self.db.query(ProveedorContactosModel).filter(
            ProveedorContactosModel.id_proveedor_contacto == id_contacto
        ).first()

        return contacto.nombre if contacto else f"ID:{id_contacto}"

    def _resolver_cambio_proveedor(self, cambio_proveedor: Optional[str]) -> Optional[str]:
        """Resuelve el cambio de proveedor de IDs a nombres"""
        if not cambio_proveedor:
            return None

        id_anterior, id_nuevo = _parsear_cambio_concatenado(cambio_proveedor)

        if id_anterior and id_nuevo:
            nombre_anterior = self._obtener_nombre_proveedor(id_anterior)
            nombre_nuevo = self._obtener_nombre_proveedor(id_nuevo)
            return f"{nombre_anterior} ----> {nombre_nuevo}"
        elif id_nuevo:
            return self._obtener_nombre_proveedor(id_nuevo)
        else:
            return None

    def _resolver_cambio_contacto(self, cambio_contacto: Optional[str]) -> Optional[str]:
        """Resuelve el cambio de contacto de IDs a nombres"""
        if not cambio_contacto:
            return None

        id_anterior, id_nuevo = _parsear_cambio_concatenado(cambio_contacto)

        if id_anterior and id_nuevo:
            nombre_anterior = self._obtener_nombre_contacto(id_anterior)
            nombre_nuevo = self._obtener_nombre_contacto(id_nuevo)
            return f"{nombre_anterior} ----> {nombre_nuevo}"
        elif id_nuevo:
            return self._obtener_nombre_contacto(id_nuevo)
        else:
            return None

    def _resolver_productos(self, productos_json: Optional[str]) -> Optional[List[str]]:
        """Resuelve una lista de IDs de productos a nombres, preservando duplicados"""
        if not productos_json:
            return None

        try:
            ids_raw = json.loads(productos_json)
            if not ids_raw:
                return None

            # Convertir IDs a integers (pueden venir como strings desde el JSON)
            ids = []
            for id_val in ids_raw:
                try:
                    ids.append(int(id_val))
                except (ValueError, TypeError):
                    logger.warning(f"ID de producto inválido: {id_val}")
                    ids.append(id_val)

            # Obtener IDs únicos para la consulta
            ids_unicos = list(set(ids))

            # Consultar todos los nombres de una vez
            productos = self.db.query(ProductosModel).filter(
                ProductosModel.id_producto.in_(ids_unicos)
            ).all()

            # Crear un mapa de id -> nombre
            mapa_productos = {p.id_producto: p.nombre for p in productos}

            # Mapear cada ID del array original a su nombre, preservando duplicados
            nombres = [mapa_productos.get(id_prod, f"ID:{id_prod}") for id_prod in ids]

            return nombres if nombres else None

        except Exception as e:
            logger.error(f"Error al parsear productos JSON: {e}")
            return None

    def _resolver_productos_modificados(self, productos_json: Optional[str]) -> Optional[List[Dict[str, Any]]]:
        """Resuelve productos modificados incluyendo sus cambios"""
        if not productos_json:
            return None

        try:
            productos_data = json.loads(productos_json)
            if not productos_data:
                return None

            resultado = []
            for item in productos_data:
                id_producto_raw = item.get('id_producto')
                cambios = item.get('cambios', {})

                # Convertir ID a integer (puede venir como string desde el JSON)
                try:
                    id_producto = int(id_producto_raw)
                except (ValueError, TypeError):
                    logger.warning(f"ID de producto inválido en modificados: {id_producto_raw}")
                    id_producto = id_producto_raw

                # Obtener nombre del producto
                producto = self.db.query(ProductosModel).filter(
                    ProductosModel.id_producto == id_producto
                ).first()

                nombre = producto.nombre if producto else f"ID:{id_producto}"

                resultado.append({
                    'nombre': nombre,
                    'cambios': cambios
                })

            return resultado if resultado else None

        except Exception as e:
            logger.error(f"Error al parsear productos modificados JSON: {e}")
            return None

    def execute(
        self,
        id_orden_compra: Optional[int] = None,
        numero_oc: Optional[str] = None,
        tipo_operacion: Optional[str] = None,
        usuario: Optional[str] = None,
        proveedor: Optional[str] = None,
        ruc_proveedor: Optional[str] = None,
        contacto: Optional[str] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        Ejecuta el caso de uso de listado de auditorías con JOINs.

        Args:
            id_orden_compra: Filtrar por ID de orden de compra
            numero_oc: Filtrar por número de OC
            tipo_operacion: Filtrar por tipo de operación
            usuario: Buscar por nombre del usuario
            proveedor: Buscar por razón social del proveedor
            ruc_proveedor: Filtrar por RUC del proveedor
            contacto: Buscar por nombre del contacto
            fecha_desde: Filtrar desde esta fecha
            fecha_hasta: Filtrar hasta esta fecha
            page: Número de página
            page_size: Cantidad de registros por página

        Returns:
            dict: Diccionario con auditorías procesadas y metadatos de paginación
        """
        try:
            logger.info(f"Listando auditorías - Página {page}, tamaño {page_size}")

            # Query base con LEFT JOINs para incluir todas las auditorías
            query = (
                self.db.query(
                    OrdenesCompraAuditoriaModel,
                    OrdenesCompraModel.correlative.label("numero_oc"),
                    func.concat(TrabajadoresModel.nombre, ' ', TrabajadoresModel.apellido).label("nombre_usuario")
                )
                .outerjoin(OrdenesCompraModel, OrdenesCompraAuditoriaModel.id_orden_compra == OrdenesCompraModel.id_orden)
                .outerjoin(UsuariosModel, OrdenesCompraAuditoriaModel.id_usuario == UsuariosModel.id_usuario)
                .outerjoin(TrabajadoresModel, UsuariosModel.id_trabajador == TrabajadoresModel.id_trabajador)
            )

            # Aplicar filtros
            filters = []

            if id_orden_compra is not None:
                filters.append(OrdenesCompraAuditoriaModel.id_orden_compra == id_orden_compra)

            if numero_oc:
                filters.append(OrdenesCompraModel.correlative.like(f"%{numero_oc}%"))

            if tipo_operacion:
                filters.append(OrdenesCompraAuditoriaModel.tipo_operacion == tipo_operacion.upper())

            if usuario:
                usuario_filter = or_(
                    UsuariosModel.username.like(f"%{usuario}%"),
                    TrabajadoresModel.nombre.like(f"%{usuario}%"),
                    TrabajadoresModel.apellido.like(f"%{usuario}%"),
                    func.concat(TrabajadoresModel.nombre, ' ', TrabajadoresModel.apellido).like(f"%{usuario}%")
                )
                filters.append(usuario_filter)

            # Filtros de proveedor/contacto: buscar en campos concatenados
            if proveedor:
                filters.append(OrdenesCompraAuditoriaModel.cambio_proveedor.like(f"%{proveedor}%"))

            if ruc_proveedor:
                # Obtener nombre del proveedor por RUC y buscar en cambio_proveedor
                proveedor_obj = self.db.query(ProveedoresModel).filter(
                    ProveedoresModel.ruc == ruc_proveedor
                ).first()
                if proveedor_obj:
                    filters.append(OrdenesCompraAuditoriaModel.cambio_proveedor.like(f"%{proveedor_obj.id_proveedor}%"))

            if contacto:
                filters.append(OrdenesCompraAuditoriaModel.cambio_contacto.like(f"%{contacto}%"))

            if fecha_desde:
                filters.append(OrdenesCompraAuditoriaModel.fecha_evento >= fecha_desde)

            if fecha_hasta:
                filters.append(OrdenesCompraAuditoriaModel.fecha_evento <= fecha_hasta)

            if filters:
                query = query.filter(and_(*filters))

            # Total de registros
            total = query.count()

            # Calcular paginación
            total_pages = math.ceil(total / page_size) if total > 0 else 1

            if page > total_pages and total > 0:
                logger.warning(f"Página {page} excede total {total_pages}, ajustando")
                page = total_pages

            offset = (page - 1) * page_size

            # Ordenar y paginar
            query = query.order_by(desc(OrdenesCompraAuditoriaModel.fecha_evento))
            resultados = query.limit(page_size).offset(offset).all()

            # Procesar resultados y resolver nombres
            items_procesados = []
            for auditoria, numero_oc, nombre_usuario in resultados:
                # Resolver cambios concatenados
                cambio_proveedor_resuelto = self._resolver_cambio_proveedor(auditoria.cambio_proveedor)
                cambio_contacto_resuelto = self._resolver_cambio_contacto(auditoria.cambio_contacto)

                # Resolver productos
                productos_agregados_nombres = self._resolver_productos(auditoria.productos_agregados)
                productos_modificados_data = self._resolver_productos_modificados(auditoria.productos_modificados)
                productos_eliminados_nombres = self._resolver_productos(auditoria.productos_eliminados)

                # Parsear cambios adicionales y convertir todos los valores a string
                cambios_adicionales_dict = None
                if auditoria.cambios_adicionales:
                    try:
                        raw_dict = json.loads(auditoria.cambios_adicionales)
                        # Convertir todos los valores a string para cumplir con Dict[str, str]
                        cambios_adicionales_dict = {
                            k: str(v) if not isinstance(v, str) else v
                            for k, v in raw_dict.items()
                        }
                    except:
                        pass

                # Construir item de respuesta
                # Manejar valores None para campos obligatorios del schema
                item = {
                    "id_auditoria": auditoria.id_auditoria,
                    "fecha_evento": auditoria.fecha_evento,
                    "tipo_operacion": auditoria.tipo_operacion,
                    "numero_oc": numero_oc if numero_oc is not None else "N/A",
                    "nombre_usuario": nombre_usuario if nombre_usuario is not None else "Sin asignar",
                    "cambio_proveedor": cambio_proveedor_resuelto,
                    "cambio_contacto": cambio_contacto_resuelto,
                    "cambio_monto": auditoria.cambio_monto,
                    "productos_agregados": productos_agregados_nombres,
                    "productos_modificados": productos_modificados_data,
                    "productos_eliminados": productos_eliminados_nombres,
                    "cambios_adicionales": cambios_adicionales_dict,
                    "descripcion": auditoria.descripcion
                }

                items_procesados.append(item)

            logger.info(f"✅ {len(items_procesados)} auditorías procesadas de {total} totales")

            return {
                "total": total,
                "items": items_procesados,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }

        except Exception as e:
            logger.error(f"❌ Error al listar auditorías: {e}", exc_info=True)
            raise
