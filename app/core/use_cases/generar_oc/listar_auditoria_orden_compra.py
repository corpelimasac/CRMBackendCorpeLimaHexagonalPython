import logging
import math
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, or_
from app.adapters.outbound.database.models.ordenes_compra_auditoria_model import OrdenesCompraAuditoriaModel

logger = logging.getLogger(__name__)


class ListarAuditoriaOrdenCompra:
    """
    Caso de uso para listar auditorías de órdenes de compra.

    Este caso de uso:
    1. Permite filtrar por diferentes criterios (OC, proveedor, contacto, RUC, tipo operación, fechas)
    2. Soporta paginación por número de página
    3. Retorna el historial completo de cambios en las órdenes de compra

    Siguiendo la arquitectura hexagonal:
    - Capa de aplicación (use case)
    - Se comunica con la base de datos directamente (consulta simple)
    """

    def __init__(self, db: Session):
        """
        Inicializa el caso de uso con las dependencias necesarias.

        Args:
            db: Sesión de base de datos
        """
        self.db = db

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
        Ejecuta el caso de uso de listado de auditorías.

        Args:
            id_orden_compra: Filtrar por ID de orden de compra
            numero_oc: Filtrar por número de OC (correlativo) - búsqueda parcial
            tipo_operacion: Filtrar por tipo de operación (CREACION, ACTUALIZACION, ELIMINACION)
            usuario: Buscar por nombre del usuario - búsqueda parcial
            proveedor: Buscar por razón social del proveedor - búsqueda parcial
            ruc_proveedor: Filtrar por RUC del proveedor
            contacto: Buscar por nombre del contacto - búsqueda parcial
            fecha_desde: Filtrar desde esta fecha
            fecha_hasta: Filtrar hasta esta fecha
            page: Número de página (default: 1)
            page_size: Cantidad de registros por página (default: 10, max: 100)

        Returns:
            dict: Diccionario con el total de registros, items y metadatos de paginación
        """
        try:
            logger.info(f"Listando auditorías de órdenes de compra - Página {page}, tamaño {page_size}")
            logger.info(f"Filtros: id_orden={id_orden_compra}, numero_oc={numero_oc}, tipo={tipo_operacion}, "
                       f"usuario={usuario}, proveedor={proveedor}, ruc={ruc_proveedor}, contacto={contacto}")

            # Construir query base
            query = self.db.query(OrdenesCompraAuditoriaModel)

            # Aplicar filtros
            filters = []

            # Filtro por ID de orden
            if id_orden_compra is not None:
                filters.append(OrdenesCompraAuditoriaModel.id_orden_compra == id_orden_compra)

            # Filtro por número de OC (correlativo) - búsqueda parcial
            if numero_oc:
                filters.append(OrdenesCompraAuditoriaModel.numero_oc.like(f"%{numero_oc}%"))

            # Filtro por tipo de operación
            if tipo_operacion:
                filters.append(OrdenesCompraAuditoriaModel.tipo_operacion == tipo_operacion.upper())

            # Filtro por usuario - buscar por nombre de usuario, nombre o apellido
            if usuario:
                from app.adapters.outbound.database.models.usuarios_model import UsuariosModel
                from sqlalchemy import func, concat

                # Subquery para buscar IDs de usuarios que coincidan con el nombre
                usuario_ids_subquery = self.db.query(UsuariosModel.id_usuario).filter(
                    or_(
                        UsuariosModel.username.like(f"%{usuario}%"),
                        UsuariosModel.nombre.like(f"%{usuario}%"),
                        UsuariosModel.apellido.like(f"%{usuario}%"),
                        concat(UsuariosModel.nombre, ' ', UsuariosModel.apellido).like(f"%{usuario}%")
                    )
                ).scalar_subquery()

                filters.append(OrdenesCompraAuditoriaModel.id_usuario.in_(
                    self.db.query(UsuariosModel.id_usuario).filter(
                        or_(
                            UsuariosModel.username.like(f"%{usuario}%"),
                            UsuariosModel.nombre.like(f"%{usuario}%"),
                            UsuariosModel.apellido.like(f"%{usuario}%"),
                            concat(UsuariosModel.nombre, ' ', UsuariosModel.apellido).like(f"%{usuario}%")
                        )
                    )
                ))

            # Filtro por proveedor - buscar en campos anterior y nuevo
            if proveedor:
                proveedor_filter = or_(
                    OrdenesCompraAuditoriaModel.proveedor_anterior.like(f"%{proveedor}%"),
                    OrdenesCompraAuditoriaModel.proveedor_nuevo.like(f"%{proveedor}%")
                )
                filters.append(proveedor_filter)

            # Filtro por RUC del proveedor
            # Nota: El RUC no está directamente en la tabla de auditoría,
            # pero podemos buscar por el nombre del proveedor asociado al RUC
            if ruc_proveedor:
                # Necesitamos hacer un subquery para buscar el nombre del proveedor por RUC
                from app.adapters.outbound.database.models.proveedores_model import ProveedoresModel
                proveedor_subquery = self.db.query(ProveedoresModel.razon_social).filter(
                    ProveedoresModel.ruc == ruc_proveedor
                ).scalar_subquery()

                ruc_filter = or_(
                    OrdenesCompraAuditoriaModel.proveedor_anterior.in_([proveedor_subquery]),
                    OrdenesCompraAuditoriaModel.proveedor_nuevo.in_([proveedor_subquery])
                )
                filters.append(ruc_filter)

            # Filtro por contacto - buscar en campos anterior y nuevo
            if contacto:
                contacto_filter = or_(
                    OrdenesCompraAuditoriaModel.contacto_anterior.like(f"%{contacto}%"),
                    OrdenesCompraAuditoriaModel.contacto_nuevo.like(f"%{contacto}%")
                )
                filters.append(contacto_filter)

            # Filtro por rango de fechas
            if fecha_desde:
                filters.append(OrdenesCompraAuditoriaModel.fecha_evento >= fecha_desde)

            if fecha_hasta:
                filters.append(OrdenesCompraAuditoriaModel.fecha_evento <= fecha_hasta)

            # Aplicar filtros si existen
            if filters:
                query = query.filter(and_(*filters))

            # Obtener total de registros
            total = query.count()

            # Calcular total de páginas
            total_pages = math.ceil(total / page_size) if total > 0 else 1

            # Validar que la página solicitada no exceda el total
            if page > total_pages and total > 0:
                logger.warning(f"Página {page} excede total de páginas {total_pages}, ajustando a última página")
                page = total_pages

            # Calcular offset basado en el número de página
            offset = (page - 1) * page_size

            # Ordenar por fecha descendente (más reciente primero)
            query = query.order_by(desc(OrdenesCompraAuditoriaModel.fecha_evento))

            # Aplicar paginación
            auditorias = query.limit(page_size).offset(offset).all()

            logger.info(f"✅ Se encontraron {total} registros totales, retornando {len(auditorias)} en página {page}/{total_pages}")

            return {
                "total": total,
                "items": auditorias,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }

        except Exception as e:
            logger.error(f"❌ Error al listar auditorías de órdenes de compra: {e}", exc_info=True)
            raise
