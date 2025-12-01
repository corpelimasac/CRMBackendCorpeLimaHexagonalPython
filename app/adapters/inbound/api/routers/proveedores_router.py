# app/adapters/inbound/api/routers/proveedores_router.py
from typing import List
from fastapi import APIRouter, Depends
from app.core.use_cases.proveedores.get_provider_contacts_use_case import GetProviderContactsUseCase
from app.dependencies import get_provider_contacts_use_case
from app.adapters.inbound.api.schemas.proveedor_schemas import ContactResponseDTO

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])

@router.get("/{id_proveedor}/contactos", response_model=List[ContactResponseDTO])
def get_provider_contacts(
    id_proveedor: int,
    use_case: GetProviderContactsUseCase = Depends(get_provider_contacts_use_case)
):
    """Obtiene todos los contactos de un proveedor específico."""
    # El caso de uso devuelve entidades de dominio, FastAPI las convierte a DTO
    return use_case.execute(id_proveedor)
