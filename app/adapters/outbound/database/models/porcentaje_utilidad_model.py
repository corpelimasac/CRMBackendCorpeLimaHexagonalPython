from sqlalchemy import Column, Integer, DECIMAL
from .base import Base

class PorcentajeUtilidadModel(Base):
  __tablename__ = "porcentaje_utilidad"
  id_porcentaje_utilidad = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
  max_precio = Column(DECIMAL(18,2), nullable=True)
  min_precio = Column(DECIMAL(18,2), nullable=True)
  porcentaje = Column(DECIMAL(5,2), nullable=True)