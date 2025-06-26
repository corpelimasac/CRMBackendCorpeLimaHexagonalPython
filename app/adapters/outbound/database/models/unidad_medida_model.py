from sqlalchemy import Column, Integer, VARCHAR, Boolean
from .base import Base

class UnidadMedidaModel(Base):
  """
  Modelo SQLAlchemy para la tabla de unidades de medida
  """
  __tablename__ = "unidad_medida"
  id_unidad_medida = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
  descripcion = Column(VARCHAR(255), nullable=True)
  estado = Column(Boolean, default=True, nullable=True)






