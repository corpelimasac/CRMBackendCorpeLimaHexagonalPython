
from app.adapters.inbound.api.schemas.end_quotation_schemas import (
    GetDataEndQuotationResponse, GetDataEndQuotationDTO, ProveedorInfoDTO, ProductoDTO
)
from app.core.ports.repositories.productos_cotizaciones_repository import ProductosCotizacionesRepositoryPort
from typing import List, Dict, Any
from collections import defaultdict


def _group_by_provider(raw_data: List[Any]) -> Dict[int, Dict[str, Any]]:
    """Agrupa los datos por proveedor"""
    providers = defaultdict(lambda: {"rows": []})

    for row in raw_data:
        provider_id = row.IDPROVEEDOR
        providers[provider_id]["rows"].append(row)

    return providers


class GetFinalizedQuotationUseCase:
    def __init__(self, productos_cotizaciones_repo: ProductosCotizacionesRepositoryPort):
        self.productos_cotizaciones_repo = productos_cotizaciones_repo

    def execute(self, quotation_id: int, version_id: int) -> GetDataEndQuotationResponse:
        try:
            # 1. Obtener los datos crudos del repositorio
            raw_data = self.productos_cotizaciones_repo.obtener_productos_cotizaciones(quotation_id, version_id)
            
            if not raw_data:
                return GetDataEndQuotationResponse(
                    success=False,
                    message="No se encontraron datos para la cotización especificada",
                    data=[]
                )

            # 2. Agrupar datos por proveedor
            providers_data = _group_by_provider(raw_data)
            
            # 3. Mapear a DTOs
            response_data_dtos = []
            for provider_id, provider_data in providers_data.items():
                # Crear DTO del proveedor
                first_row = provider_data['rows'][0]  # Tomar el primer row para datos del proveedor
                proveedor_dto = ProveedorInfoDTO(
                    idProveedor=first_row.IDPROVEEDOR,
                    nombreProveedor=first_row.RAZONSOCIAL,
                    direccionProveedor=first_row.DIRECCION,
                    moneda=first_row.MONEDA,
                    entrega=first_row.ENTREGA,
                    pago=first_row.PAGO
                )
                
                # Crear DTOs de productos
                productos_dtos = []
                for index, row in enumerate(provider_data['rows']):
                    producto_dto = ProductoDTO(
                        id=row.IDPRODUCTO,  # Usando un índice secuencial como ID del producto
                        cant=row.CANT,
                        und=row.UMED if row.UMED else "N/A",
                        nombre=row.PRODUCTO if row.PRODUCTO else "N/A",
                        marca=row.MARCA if row.MARCA else "N/A",
                        modelo=row.MODELO if row.MODELO else "N/A",
                        punitario=float(row.PUNIT) if row.PUNIT else 0.0,
                        ptotal=float(row.PTOTAL) if row.PTOTAL else 0.0,
                        igv=row.IGV if row.IGV else "N/A",
                        idProductoCotizacion=row.IDPRODUCTOCOTIZACION
                    )
                    productos_dtos.append(producto_dto)
                
                # Crear el DTO principal
                cotizacion_dto = GetDataEndQuotationDTO(
                    proveedorInfo=[proveedor_dto],
                    productos=productos_dtos
                )
                response_data_dtos.append(cotizacion_dto)

            # 4. Construir la respuesta final
            return GetDataEndQuotationResponse(
                success=True,
                message="Informacion de la cotizacion finalizada obtenida correctamente",
                data=response_data_dtos
            )
            
        except Exception as e:
            print(f"Error en GetFinalizedQuotationUseCase: {e}")
            return GetDataEndQuotationResponse(
                success=False,
                message=f"Error al obtener la información de la cotización: {str(e)}",
                data=[]
            )

