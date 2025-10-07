from app.core.ports.repositories.tipo_cambio_repository import TipoCambioRepositoryPort
from app.adapters.outbound.database.models.tasa_cambio_sunat_model import TasaCambioSunatModel
from sqlalchemy.orm import Session
from decimal import Decimal
from typing import Optional
from datetime import date
import logging

logger = logging.getLogger(__name__)


class TipoCambioRepository(TipoCambioRepositoryPort):
    """
    Implementación del repositorio de tipo de cambio SUNAT
    """

    def __init__(self, db: Session):
        self.db = db

    def obtener_tipo_cambio_mas_reciente(self) -> Optional[Decimal]:
        """
        Obtiene el tipo de cambio (venta) más reciente de SUNAT

        Equivalente a: findTopByOrderByFechaDesc().map(TasaCambioSunat::getVenta)

        Returns:
            Decimal: Tipo de cambio venta, None si no hay datos
        """
        try:
            tasa = self.db.query(TasaCambioSunatModel).order_by(
                TasaCambioSunatModel.fecha.desc()
            ).first()

            if tasa:
                logger.info(f"Tipo de cambio obtenido: {tasa.venta} (fecha: {tasa.fecha})")
                return tasa.venta
            else:
                logger.warning("No se encontró tipo de cambio en la base de datos")
                return None

        except Exception as e:
            logger.error(f"Error al obtener tipo de cambio: {e}")
            return None

    def obtener_tipo_cambio_por_fecha(self, fecha: date) -> Optional[Decimal]:
        """
        Obtiene el tipo de cambio (venta) para una fecha específica

        Args:
            fecha: Fecha del tipo de cambio

        Returns:
            Decimal: Tipo de cambio venta, None si no hay datos
        """
        try:
            tasa = self.db.query(TasaCambioSunatModel).filter(
                TasaCambioSunatModel.fecha == fecha
            ).first()

            if tasa:
                logger.info(f"Tipo de cambio para {fecha}: {tasa.venta}")
                return tasa.venta
            else:
                logger.warning(f"No se encontró tipo de cambio para la fecha {fecha}")
                return None

        except Exception as e:
            logger.error(f"Error al obtener tipo de cambio por fecha: {e}")
            return None
