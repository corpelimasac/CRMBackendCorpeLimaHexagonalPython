# app/core/use_cases/proveedores/get_provider_contacts_use_case.py
from typing import List
from app.core.ports.repositories.proveedores_repository_port import ProveedoresRepositoryPort
from app.core.domain.entities.proveedor_contacto import ProveedorContacto
from app.adapters.inbound.api.schemas.proveedor_schemas import ContactResponseDTO

class GetProviderContactsUseCase:
    def __init__(self, provider_repo: ProveedoresRepositoryPort):
        self.provider_repo = provider_repo

    def execute(self, provider_id: int) -> List[ContactResponseDTO  ]:
        # 1. Obtiene las entidades de dominio
        domain_contacts = self.provider_repo.obtener_contacto_proveedor(provider_id)
# 2. Realiza el mapeo a DTOs AQUÍ DENTRO
        response_dtos = [
            ContactResponseDTO(
                id_proveedor_contacto=c.id_proveedor_contacto,
                nombre=c.nombre,
                telefono=c.telefono,
                celular=c.celular,
                correo=c.correo
            ) for c in domain_contacts
        ]
        return response_dtos