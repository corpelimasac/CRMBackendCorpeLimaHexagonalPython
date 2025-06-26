from sqlalchemy import Column, Integer, BIGINT,  VARCHAR, BIT, Date, Enum, ForeignKey
from datetime import datetime
from .base import Base

class CotizacionesVersionesModel(Base):
  __tablename__ = "cotizaciones_versiones"
  id_cotizacion_versiones = Column(BIGINT, primary_key=True, index=True, autoincrement=True, nullable=False)
  fecha_creacion = Column(Date, default=datetime.now, nullable=False)

  ruta_s3 = Column(VARCHAR(255), nullable=True)
  version_cotizacion = Column(Integer, nullable=False)
  estado = Column(Enum('EN_DESCUENTO','FINALIZADA','INICIAL'), nullable=True)
  fecha_modificacion = Column(Date, default=datetime.now, onupdate=datetime.now, nullable=True)
  
  # Relación con la tabla de cotizaciones
  id_cotizacion = Column(BIGINT,ForeignKey("cotizacion.id_cotizacion"), nullable=False)