"""
Router para la integración con SUNAT
"""
from fastapi import APIRouter, HTTPException, Depends
from app.adapters.inbound.api.schemas.sunat_schemas import SunatRucResponse, SunatErrorResponse
from app.core.use_cases.integracion_sunat.integracion_sunat_uc import IntegracionSunatUC
from app.adapters.outbound.external_services.sunat.sunat_scraper import SunatScrapper
from typing import Union

router = APIRouter(prefix="/integracion-sunat", tags=["Integración con Sunat"])


def get_sunat_use_case() -> IntegracionSunatUC:
    """
    Dependencia para obtener el caso de uso de SUNAT
    """
    import os
    # Usar headless=True en producción (Railway/Docker) y headless=False en local
    # Railway y otros entornos cloud suelen definir PORT o RAILWAY_ENVIRONMENT
    is_production = os.getenv('RAILWAY_ENVIRONMENT') is not None or os.path.exists('/.dockerenv')
    sunat_scraper = SunatScrapper(headless=is_production)
    return IntegracionSunatUC(sunat_scraper)


@router.get(
    "/obtener-ruc/{ruc}",
    response_model=Union[SunatRucResponse, SunatErrorResponse],
    summary="Consultar información de RUC en SUNAT",
    description="Consulta información completa de un RUC en la página web de SUNAT mediante web scraping",
    responses={
        200: {
            "description": "Información del RUC obtenida exitosamente",
            "model": SunatRucResponse
        },
        400: {
            "description": "Error en la validación del RUC",
            "model": SunatErrorResponse
        },
        500: {
            "description": "Error interno del servidor",
            "model": SunatErrorResponse
        }
    }
)
async def obtener_ruc(
    ruc: str,
    use_case: IntegracionSunatUC = Depends(get_sunat_use_case)
) -> Union[SunatRucResponse, SunatErrorResponse]:
    """
    Consulta información de un RUC en SUNAT
    
    Args:
        ruc (str): Número de RUC a consultar (11 dígitos)
        
    Returns:
        Union[SunatRucResponse, SunatErrorResponse]: Información del RUC o error
        
    Raises:
        HTTPException: Si hay errores en la consulta
        :param ruc:
        :param use_case:
    """
    try:
        resultado = await use_case.obtener_ruc(ruc)
        
        # Verificar si es una respuesta de error
        if "message" in resultado and "detail" in resultado:
            raise HTTPException(
                status_code=400 if "formato" in resultado["detail"] else 500,
                detail=resultado
            )
        
        return SunatRucResponse(**resultado)
        
    except HTTPException:
        # Re-lanzar HTTPException para que FastAPI la maneje
        raise
    except Exception as e:
        # Capturar cualquier otro error no previsto
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Error interno del servidor",
                "detail": f"Error inesperado al consultar el RUC {ruc}: {str(e)}",
                "ruc": ruc
            }
        )

