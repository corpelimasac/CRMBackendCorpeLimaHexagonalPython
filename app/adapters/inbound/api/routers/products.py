"""
Router de Productos
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/products")
async def get_products():
    """
    Obtener lista de productos
    """
    # TODO: Implementar lógica usando casos de uso
    return {"message": "Lista de productos", "products": []}


@router.post("/products")
async def create_product():
    """
    Crear un nuevo producto
    """
    # TODO: Implementar lógica usando casos de uso
    return {"message": "Producto creado"}


@router.get("/products/{product_id}")
async def get_product(product_id: int):
    """
    Obtener un producto por ID
    """
    # TODO: Implementar lógica usando casos de uso
    return {"message": f"Producto {product_id}", "product": {}} 