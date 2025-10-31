from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from typing import List
import logging

from app.adapters.outbound.database.models.proveedor_contacto_model import (
    ProveedorContactosModel,
    intermedia_proveedor_contacto,
)
from app.core.ports.repositories.proveedores_repository_port import ProveedoresRepositoryPort
from app.core.domain.entities.proveedor_contacto import ProveedorContacto

logger = logging.getLogger(__name__)


class ProveedoresRepository(ProveedoresRepositoryPort):
    """Repositorio para manejar las operaciones de base de datos relacionadas con los proveedores"""

    def __init__(self, db: Session):
        self.db = db

    def obtener_contacto_proveedor(self, provider_id: int) -> List[ProveedorContacto]:
        """
        Obtiene los contactos activos de un proveedor

        Args:
            provider_id: ID del proveedor

        Returns:
            List[ProveedorContacto]: Lista de contactos del proveedor
        """
        logger.info(f"Obteniendo contactos del proveedor {provider_id}")

        # --- Construcción del query SQLAlchemy Core ---
        stmt = (
            select(ProveedorContactosModel)
            .join(intermedia_proveedor_contacto)
            .where(
                and_(
                    intermedia_proveedor_contacto.c.id_proveedor == provider_id,
                    ProveedorContactosModel.estado.is_(True),
                )
            )
        )

        # --- Ejecución ---
        result = self.db.execute(stmt).scalars().all()
        logger.debug(f"Modelos encontrados: {len(result)} contactos")

        # --- Conversión a entidades de dominio ---
        contacts = [
            ProveedorContacto(
                id_proveedor_contacto=c.id_proveedor_contacto,
                nombre=c.nombre,
                telefono=c.telefono,
                celular=c.celular,
                correo=c.correo,
                sexo=c.sexo,
                cargo=c.cargo,
                observacion=c.observacion,
            )
            for c in result
        ]

        logger.info(f"Se obtuvieron {len(contacts)} contactos del proveedor {provider_id}")
        return contacts
