"""
Caso de uso para obtener información de cotización finalizada.

Este caso de uso obtiene los productos disponibles de una cotización
y los agrupa por proveedor para su presentación.
"""
from typing import List, Dict
from collections import defaultdict

from app.adapters.inbound.api.schemas.end_quotation_schemas import (
    GetDataEndQuotationResponse, GetDataEndQuotationDTO, ProveedorInfoDTO, ProductoDTO
)
from app.core.ports.repositories.productos_cotizaciones_repository import ProductosCotizacionesRepositoryPort
from app.core.domain.dtos.producto_cotizacion_dtos import ProductoCotizacionDisponible


def _group_by_provider(
    productos: List[ProductoCotizacionDisponible]
) -> Dict[int, List[ProductoCotizacionDisponible]]:
    """
    Agrupa los productos por proveedor.

    Args:
        productos: Lista de productos disponibles

    Returns:
        Dict[int, List[ProductoCotizacionDisponible]]: Productos agrupados por ID de proveedor
    """
    providers: Dict[int, List[ProductoCotizacionDisponible]] = defaultdict(list)

    for producto in productos:
        providers[producto.id_proveedor].append(producto)

    return providers


class GetFinalizedQuotationUseCase:
    """
    Caso de uso para obtener información de cotización finalizada.

    Responsabilidad: Obtener productos disponibles y agruparlos por proveedor.
    """

    def __init__(self, productos_cotizaciones_repo: ProductosCotizacionesRepositoryPort):
        """
        Inicializa el caso de uso.

        Args:
            productos_cotizaciones_repo: Repositorio de productos de cotizaciones
        """
        self.productos_cotizaciones_repo = productos_cotizaciones_repo

    def execute(self, quotation_id: int, version_id: int) -> GetDataEndQuotationResponse:
        """
        Ejecuta el caso de uso para obtener cotización finalizada.

        Args:
            quotation_id: ID de la cotización
            version_id: ID de la versión de la cotización

        Returns:
            GetDataEndQuotationResponse: Respuesta con productos agrupados por proveedor
        """
        try:
            # 1. Obtener productos disponibles del repositorio (con tipado fuerte)
            productos_disponibles = self.productos_cotizaciones_repo.obtener_productos_cotizaciones(
                quotation_id, version_id
            )

            if not productos_disponibles:
                return GetDataEndQuotationResponse(
                    success=False,
                    message="No se encontraron datos para la cotización especificada",
                    data=[]
                )

            # 2. Agrupar productos por proveedor
            productos_por_proveedor = _group_by_provider(productos_disponibles)

            # 3. Mapear DTOs del dominio a DTOs de API
            response_data_dtos: List[GetDataEndQuotationDTO] = []

            for provider_id, productos in productos_por_proveedor.items():
                # Tomar el primer producto para obtener datos del proveedor
                primer_producto = productos[0]

                # Crear DTO del proveedor (del adaptador de API)
                proveedor_dto = ProveedorInfoDTO(
                    idProveedor=primer_producto.id_proveedor,
                    nombreProveedor=primer_producto.razon_social,
                    direccionProveedor=primer_producto.direccion or "",
                    moneda=primer_producto.moneda,
                    entrega=primer_producto.entrega or "",
                    pago=primer_producto.pago or ""
                )

                # Crear DTOs de productos (del adaptador de API)
                productos_dtos: List[ProductoDTO] = []
                for producto in productos:
                    producto_dto = ProductoDTO(
                        id=producto.id_producto,
                        cant=float(producto.cantidad),
                        und=producto.unidad_medida,
                        nombre=producto.producto,
                        marca=producto.marca or "N/A",
                        modelo=producto.modelo or "N/A",
                        punitario=float(producto.precio_unitario),
                        ptotal=float(producto.precio_total),
                        igv=producto.igv,
                        idProductoCotizacion=producto.id_producto_cotizacion
                    )
                    productos_dtos.append(producto_dto)

                # Crear el DTO principal de cotización
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

