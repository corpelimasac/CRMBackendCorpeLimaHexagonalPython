from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime


@dataclass
class RepresentanteLegalDTO:
    """DTO para información del representante legal"""
    tipo_documento: str = "Sin datos"
    nro_documento: str = "Sin datos"
    nombre: str = "Sin datos"
    cargo: str = "Sin datos"
    fecha_desde: str = "Sin datos"

    def to_dict(self) -> dict:
        """Convierte el DTO a diccionario con nombres snake_case"""
        return {
            "tipoDocumento": self.tipo_documento,
            "nroDocumento": self.nro_documento,
            "nombre": self.nombre,
            "cargo": self.cargo,
            "fechaDesde": self.fecha_desde
        }


@dataclass
class DatosRucDTO:
    """DTO principal para toda la información del RUC"""
    numero_documento: str
    razon_social: str = "Sin datos"
    nombre_comercial: str = "Sin datos"
    tipo_contribuyente: str = "Sin datos"
    fecha_inicio_actividades: str = "Sin datos"
    activo: bool = False
    condicion_contribuyente: str = "Sin datos"
    direccion: str = "Sin datos"
    distrito: str = "Sin datos"
    provincia: str = "Sin datos"
    departamento: str = "Sin datos"
    ubigeo: str = "Sin ubigeo"
    actividad_economica: str = "Sin datos"
    actividad_economica2: str = "No tiene"
    es_agente_retencion: bool = False
    numero_trabajadores: str = "0"
    prestadores_de_servicios: str = "0"
    representante_legal: RepresentanteLegalDTO = field(default_factory=RepresentanteLegalDTO)
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Convierte el DTO a diccionario con el formato esperado"""
        return {
            "numeroDocumento": self.numero_documento,
            "razonSocial": self.razon_social,
            "nombreComercial": self.nombre_comercial,
            "tipoContribuyente": self.tipo_contribuyente,
            "fechaInicioActividades": self.fecha_inicio_actividades,
            "activo": self.activo,
            "condicionContribuyente": self.condicion_contribuyente,
            "direccion": self.direccion,
            "distrito": self.distrito,
            "provincia": self.provincia,
            "departamento": self.departamento,
            "ubigeo": self.ubigeo,
            "actividadEconomica": self.actividad_economica,
            "actividadEconomica2": self.actividad_economica2,
            "EsAgenteRetencion": self.es_agente_retencion,
            "numeroTrabajadores": self.numero_trabajadores,
            "prestadoresdeServicios": self.prestadores_de_servicios,
            "representanteLegal": self.representante_legal.to_dict(),
            **({"error": self.error} if self.error else {})
        }

    @classmethod
    def crear_error(cls, numero_documento: str, mensaje_error: str) -> 'DatosRucDTO':
        """Factory method para crear una respuesta de error"""
        return cls(
            numero_documento=numero_documento,
            razon_social="Error en consulta",
            error=mensaje_error
        )
