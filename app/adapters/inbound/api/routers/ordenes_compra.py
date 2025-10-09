from fastapi import APIRouter
from app.adapters.inbound.api.schemas.ordenes_compra_schemas import OrdenesCompraRequest
from app.core.use_cases.generar_oc.generar_orden_compra import GenerarOrdenCompra
from fastapi import Depends
from app.dependencies import get_generate_purchase_order_use_case
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ordenes-compra", tags=["Ordenes de Compra"])

@router.post("/generar")
async def create_order(order: OrdenesCompraRequest, use_case: GenerarOrdenCompra = Depends(get_generate_purchase_order_use_case)):
    try:
        logger.info("=" * 80)
        logger.info("🚀 INICIO - Creación de órdenes de compra")
        logger.info(f"📦 Request: {len(order.data)} órdenes a procesar")
        print("=" * 80)
        print("🚀 INICIO - Creación de órdenes de compra")
        print(f"📦 Request: {len(order.data)} órdenes a procesar")
        
        urls = await use_case.execute(order)
        
        logger.info(f"✅ FIN - {len(urls)} URLs generadas")
        logger.info("=" * 80)
        print(f"✅ FIN - {len(urls)} URLs generadas")
        print("=" * 80)
        return {"status": "Órdenes de compra generadas", "urls": urls}
    except Exception as e:
        logger.error(f"❌ ERROR en create_order: {e}")
        logger.error(f"Tipo de error: {type(e)}")
        import traceback
        logger.error(traceback.format_exc())
        print(f"❌ ERROR en create_order: {e}")
        raise

