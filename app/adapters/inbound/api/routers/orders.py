"""
Router de Órdenes
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/orders")
async def get_orders():
    """
    Obtener lista de órdenes
    """
    # TODO: Implementar lógica usando casos de uso
    return {"message": "Lista de órdenes", "orders": []}


@router.post("/orders")
async def create_order():
    """
    Crear una nueva orden
    """
    # TODO: Implementar lógica usando casos de uso
    return {"message": "Orden creada"}


@router.get("/orders/{order_id}")
async def get_order(order_id: int):
    """
    Obtener una orden por ID
    """
    # TODO: Implementar lógica usando casos de uso
    return {"message": f"Orden {order_id}", "order": {}} 