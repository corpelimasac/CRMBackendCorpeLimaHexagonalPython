from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class OrdenCompraAuditoriaResponse(BaseModel):
    """Schema para la respuesta de una auditoría de orden de compra"""

    id_auditoria: int = Field(..., description="ID de la auditoría")
    fecha_evento: datetime = Field(..., description="Fecha y hora del evento")
    tipo_operacion: str = Field(..., description="Tipo de operación: CREACION, ACTUALIZACION, ELIMINACION")

    # Datos de la orden
    id_orden_compra: int = Field(..., description="ID de la orden de compra")
    numero_oc: str = Field(..., description="Número correlativo de la OC")
    id_usuario: int = Field(..., description="ID del usuario que realizó el cambio")

    # Relaciones
    id_cotizacion: Optional[int] = Field(None, description="ID de la cotización")
    id_cotizacion_versiones: Optional[int] = Field(None, description="ID de la versión de cotización")

    # Cambios de proveedor
    id_proveedor_anterior: Optional[int] = Field(None, description="ID del proveedor anterior")
    proveedor_anterior: Optional[str] = Field(None, description="Nombre del proveedor anterior")
    id_proveedor_nuevo: Optional[int] = Field(None, description="ID del proveedor nuevo")
    proveedor_nuevo: Optional[str] = Field(None, description="Nombre del proveedor nuevo")

    # Cambios de contacto
    id_contacto_anterior: Optional[int] = Field(None, description="ID del contacto anterior")
    contacto_anterior: Optional[str] = Field(None, description="Nombre del contacto anterior")
    id_contacto_nuevo: Optional[int] = Field(None, description="ID del contacto nuevo")
    contacto_nuevo: Optional[str] = Field(None, description="Nombre del contacto nuevo")

    # Productos (JSON parseado)
    productos_agregados: Optional[str] = Field(None, description="Productos agregados (JSON)")
    productos_modificados: Optional[str] = Field(None, description="Productos modificados (JSON)")
    productos_eliminados: Optional[str] = Field(None, description="Productos eliminados (JSON)")

    # Montos
    monto_anterior: Optional[float] = Field(None, description="Monto anterior")
    monto_nuevo: Optional[float] = Field(None, description="Monto nuevo")

    # Otros cambios
    cambios_adicionales: Optional[str] = Field(None, description="Otros cambios (JSON)")

    # Descripción
    descripcion: str = Field(..., description="Descripción legible del cambio")
    razon: Optional[str] = Field(None, description="Razón del cambio")
    metadata_json: Optional[str] = Field(None, description="Metadata adicional (JSON)")

    class Config:
        from_attributes = True


class ListarAuditoriasRequest(BaseModel):
    """Schema para filtrar auditorías"""

    id_orden_compra: Optional[int] = Field(None, description="Filtrar por ID de orden de compra")
    numero_oc: Optional[str] = Field(None, description="Filtrar por número de OC (correlativo)")
    tipo_operacion: Optional[str] = Field(None, description="Filtrar por tipo de operación")
    id_usuario: Optional[int] = Field(None, description="Filtrar por usuario")
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
