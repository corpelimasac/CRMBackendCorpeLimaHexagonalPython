from fastapi import APIRouter
from app.adapters.inbound.api.schemas.ordenes_compra_schemas import OrdenesCompraRequest

router = APIRouter(prefix="/ordenes-compra", tags=["Ordenes de Compra"])

@router.post("/generar")
def create_order(order: OrdenesCompraRequest):


    return order


