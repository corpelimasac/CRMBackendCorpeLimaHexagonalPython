from sqlalchemy.orm import Session
from sqlalchemy import select, exists
from typing import Optional
import logging

from app.core.ports.repositories.cotizaciones_versiones_repository import CotizacionVersionesRepositoryPort
from app.adapters.outbound.database.models.cotizaciones_versiones_model import CotizacionesVersionesModel

logger = logging.getLogger(__name__)


class CotizacionVersionesRepository(CotizacionVersionesRepositoryPort):
    def __init__(self, db: Session):
        self.db = db

    def exists_by_id(self, id_cotizacion_version: int) -> bool:
        """
        Verifica si existe una versión de cotización por su ID

        Args:
            id_cotizacion_version: ID de la versión de cotización

        Returns:
            bool: True si existe, False en caso contrario
        """
        logger.info(f"Verificando existencia de cotización versión {id_cotizacion_version}")

        stmt = select(exists().where(
            CotizacionesVersionesModel.id_cotizacion_versiones == id_cotizacion_version
        ))

        return self.db.scalar(stmt)

    def get_by_id(self, id_cotizacion_version: int) -> Optional[CotizacionesVersionesModel]:
        """
        Obtiene una versión de cotización por su ID

        Args:
            id_cotizacion_version: ID de la versión de cotización

        Returns:
            CotizacionesVersionesModel: Versión de cotización encontrada o None
        """
        logger.info(f"Obteniendo cotización versión {id_cotizacion_version}")

        stmt = select(CotizacionesVersionesModel).where(
            CotizacionesVersionesModel.id_cotizacion_versiones == id_cotizacion_version
        )

        return self.db.scalar(stmt)
