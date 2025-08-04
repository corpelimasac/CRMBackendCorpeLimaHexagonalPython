from fastapi import APIRouter
from app.adapters.inbound.api.schemas.ordenes_compra_schemas import OrdenesCompraRequest
from app.core.use_cases.generar_oc.generar_orden_compra import GenerarOrdenCompra
from fastapi import Depends
from app.dependencies import get_generate_purchase_order_use_case

router = APIRouter(prefix="/ordenes-compra", tags=["Ordenes de Compra"])

@router.post("/generar")
async def create_order(order: OrdenesCompraRequest, use_case: GenerarOrdenCompra = Depends(get_generate_purchase_order_use_case)):
    print("Inicio de la orden de compra")
    urls = await use_case.execute(order)
    return {"status": "Órdenes de compra generadas", "urls": urls}

