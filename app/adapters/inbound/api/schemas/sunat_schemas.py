"""
Esquemas Pydantic para el endpoint de integración con SUNAT
"""
from pydantic import BaseModel, Field
from typing import Optional


class RepresentanteLegal(BaseModel):
    """
    Esquema para la información del representante legal
    """
    tipoDocumento: str = Field(..., description="Tipo de documento del representante")
    nroDocumento: str = Field(..., description="Número de documento del representante")
    nombre: str = Field(..., description="Nombre completo del representante")
    cargo: str = Field(..., description="Cargo del representante")
    fechaDesde: str = Field(..., description="Fecha desde la cual ejerce el cargo")


class SunatRucResponse(BaseModel):
    """
    Esquema de respuesta para la consulta de RUC en SUNAT
    """
    numeroDocumento: str = Field(..., description="Número de RUC consultado")
    razonSocial: str = Field(..., description="Razón social de la empresa")
    nombreComercial: str = Field(..., description="Nombre comercial de la empresa")
    direccion: str = Field(..., description="Dirección del domicilio fiscal")
    distrito: str = Field(..., description="Distrito del domicilio fiscal")
    provincia: str = Field(..., description="Provincia del domicilio fiscal")
    departamento: str = Field(..., description="Departamento del domicilio fiscal")
    fechaInicioActividades: str = Field(..., description="Fecha de inicio de actividades")
    activo: bool = Field(..., description="Si el contribuyente está activo")
    EsAgenteRetencion: bool = Field(..., description="Si es agente de retención")
    actividadEconomica: str = Field(..., description="Actividad económica principal")
    tipoContribuyente: str = Field(..., description="Tipo de contribuyente")
    numeroTrabajadores: str = Field(..., description="Número de trabajadores")
    prestadoresdeServicios: str = Field(..., description="Número de prestadores de servicios")
    representanteLegal: RepresentanteLegal = Field(..., description="Información del representante legal")
    error: Optional[str] = Field(None, description="Mensaje de error si ocurrió algún problema")

    class Config:
        json_schema_extra = {
            "example": {
                "numeroDocumento": "20509430625",
                "razonSocial": "3B E.I.R.L.",
                "nombreComercial": "-",
                "direccion": "JR. ANTONIO BAZO NRO. 918 URB. EL PORVENIR",
                "distrito": "LA VICTORIA",
                "provincia": "LIMA",
                "departamento": "LIMA",
                "fechaInicioActividades": "17/08/2004",
                "activo": True,
                "EsAgenteRetencion": True,
                "actividadEconomica": "VENTA AL POR MAYOR NO ESPECIALIZADA",
                "tipoContribuyente": "EMPRESA INDIVIDUAL DE RESP. LTDA",
                "numeroTrabajadores": "12",
                "prestadoresdeServicios": "1",
                "representanteLegal": {
                    "tipoDocumento": "DNI",
                    "nroDocumento": "10799404",
                    "nombre": "FAROUN ALI DARWISH MOUSA MOHAMMAD DAUD",
                    "cargo": "GERENTE",
                    "fechaDesde": "17/08/2004"
                }
            }
        }


class SunatErrorResponse(BaseModel):
    """
    Esquema de respuesta para errores en la consulta de RUC
    """
    message: str = Field(..., description="Mensaje de error")
    detail: str = Field(..., description="Detalle del error")
    ruc: Optional[str] = Field(None, description="RUC que se intentó consultar")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Error al consultar RUC",
                "detail": "El RUC proporcionado no es válido o no se pudo conectar con SUNAT",
                "ruc": "20509430625"
            }
        }
