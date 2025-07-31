from app.adapters.outbound.database.models.proveedor_contacto_model import ProveedorContactosModel
from app.adapters.outbound.database.models.proveedor_contacto_model import intermedia_proveedor_contacto
from app.core.ports.repositories.proveedores_repository_port import ProveedoresRepositoryPort
from sqlalchemy.orm import Session
from typing import List, Any
from app.core.domain.entities.proveedor_contacto import ProveedorContacto

class ProveedoresRepository(ProveedoresRepositoryPort):
    """Repositorio para manejar las operaciones de base de datos relacionadas con los proveedores"""

    def __init__(self, db: Session):
        self.db = db

    def obtener_contacto_proveedor(self, provider_id: int) -> List[ProveedorContacto]:
        print(f"provider_id: {provider_id}")
        print(f"Ejecutando consulta para obtener los contactos")
        contact_models = self.db.query(ProveedorContactosModel)\
            .join(intermedia_proveedor_contacto)\
            .filter(intermedia_proveedor_contacto.c.id_proveedor == provider_id)\
            .all()

        print(f"contact_models: {contact_models}")

        contacts = []
        for c in contact_models:
            contacts.append(
                ProveedorContacto(
                    id_proveedor_contacto=c.id_proveedor_contacto,
                    nombre=c.nombre,
                    telefono=c.telefono,
                    celular=c.celular,
                    correo=c.correo,
                    sexo=c.sexo,
                    cargo=c.cargo,
                    observacion=c.observacion
                )
            )
        print(f"contacts: {contacts}")
        return contacts