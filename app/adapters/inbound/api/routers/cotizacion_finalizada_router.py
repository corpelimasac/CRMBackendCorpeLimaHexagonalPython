from fastapi import APIRouter, Depends
from app.adapters.inbound.api.schemas.end_quotation_schemas import GetDataEndQuotationResponse
from app.core.use_cases.end_quotation.get_finalized_quotation_use_case import GetFinalizedQuotationUseCase
from app.dependencies import get_finalized_quotation_use_case

router = APIRouter(prefix="/cotizacion_finalizada",
                  tags=["Cotizacion Finalizada"],
                  responses={404: {"description": "Not found"}})

@router.get("/obtener-informacion/idCotizacion/{idCotizacion}/idCotizacionVersion/{idCotizacionVersion}",
            response_model=GetDataEndQuotationResponse)
async def obtener_informacion_cotizacion_finalizada(
    idCotizacion: int,
    idCotizacionVersion: int,
    use_case: GetFinalizedQuotationUseCase = Depends(get_finalized_quotation_use_case)
) -> GetDataEndQuotationResponse:  
    """
    Retorna la información de la cotización finalizada
    
    Args:
        idCotizacion (int): ID de la cotización
        idCotizacionVersion (int): ID de la versión de la cotización
        use_case (GetFinalizedQuotationUseCase): Caso de uso inyectado
        
    Returns:
        GetDataEndQuotationResponse: Respuesta con la información de la cotización finalizada
    """
    print(f"Obteniendo información para cotización: {idCotizacion}, versión: {idCotizacionVersion}")
    
    # Ejecutar el caso de uso
    result = use_case.execute(idCotizacion, idCotizacionVersion)
    
    return result