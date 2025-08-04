from app.core.ports.repositories.cotizaciones_versiones_repository import CotizacionVersionesRepositoryPort
from app.adapters.outbound.database.models.cotizaciones_versiones_model import CotizacionesVersionesModel
from sqlalchemy.orm import Session

class CotizacionVersionesRepository(CotizacionVersionesRepositoryPort):
    def __init__(self, db: Session):
        self.db = db

    def exists_by_id(self, id_cotizacion_version: int) -> bool:
        print(f"Verificando si existe la cotización versión {id_cotizacion_version}")
        return self.db.query(CotizacionesVersionesModel).filter(CotizacionesVersionesModel.id_cotizacion_versiones == id_cotizacion_version).first() is not None

    def get_by_id(self, id_cotizacion_version: int) -> CotizacionesVersionesModel:
        pass
