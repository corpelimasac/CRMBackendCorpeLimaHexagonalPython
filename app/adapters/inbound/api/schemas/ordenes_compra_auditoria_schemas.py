from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class OrdenCompraAuditoriaResponse(BaseModel):
    """Schema optimizado para la respuesta de una auditoría de orden de compra"""

    id_auditoria: int = Field(..., description="ID de la auditoría")
    fecha_evento: datetime = Field(..., description="Fecha y hora del evento")
    tipo_operacion: str = Field(..., description="Tipo de operación: CREACION, ACTUALIZACION, ELIMINACION")

    # Datos de la orden
    numero_oc: str = Field(..., description="Número correlativo de la OC (ej: OC-000512-2025)")
    nombre_usuario: str = Field(..., description="Nombre completo del usuario (obtenido por JOIN)")

    # Cambios en formato concatenado con nombres resueltos
    cambio_proveedor: Optional[str] = Field(None, description="Cambio de proveedor: 'PROVEEDOR A ----> PROVEEDOR B' o solo nombre")
    cambio_contacto: Optional[str] = Field(None, description="Cambio de contacto: 'CONTACTO A ----> CONTACTO B' o solo nombre")
    cambio_monto: Optional[str] = Field(None, description="Cambio de monto: 'anterior ----> nuevo'")

    # Productos con nombres resueltos
    productos_agregados: Optional[List[str]] = Field(None, description="Lista de nombres de productos agregados")
    productos_modificados: Optional[List[Dict[str, Any]]] = Field(None, description="Productos modificados con detalles")
    productos_eliminados: Optional[List[str]] = Field(None, description="Lista de nombres de productos eliminados")

    # Otros cambios
    cambios_adicionales: Optional[Dict[str, str]] = Field(None, description="Otros cambios en formato 'anterior ----> nuevo'")

    # Descripción
    descripcion: str = Field(..., description="Descripción legible del cambio")

    class Config:
        from_attributes = True


class ListarAuditoriasRequest(BaseModel):
    """Schema para filtrar auditorías"""

    id_orden_compra: Optional[int] = Field(None, description="Filtrar por ID de orden de compra")
    numero_oc: Optional[str] = Field(None, description="Filtrar por número de OC (correlativo)")
    tipo_operacion: Optional[str] = Field(None, description="Filtrar por tipo de operación")
    usuario: Optional[str] = Field(None, description="Buscar por nombre del usuario")
    proveedor: Optional[str] = Field(None, description="Buscar por razón social del proveedor")
    ruc_proveedor: Optional[str] = Field(None, description="Filtrar por RUC del proveedor")
    contacto: Optional[str] = Field(None, description="Buscar por nombre del contacto")
    fecha_desde: Optional[datetime] = Field(None, description="Fecha desde")
    fecha_hasta: Optional[datetime] = Field(None, description="Fecha hasta")
    page: int = Field(1, description="Número de página", ge=1)
    page_size: int = Field(10, description="Cantidad de registros por página", ge=1, le=100)


class ListarAuditoriasResponse(BaseModel):
    """Schema para la respuesta de listado de auditorías"""

    total: int = Field(..., description="Total de registros encontrados")
    items: List[OrdenCompraAuditoriaResponse] = Field(..., description="Lista de auditorías")
    page: int = Field(..., description="Página actual")
    page_size: int = Field(..., description="Cantidad de registros por página")
    total_pages: int = Field(..., description="Total de páginas disponibles")
