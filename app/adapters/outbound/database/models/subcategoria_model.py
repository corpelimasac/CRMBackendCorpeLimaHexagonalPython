from sqlalchemy import Column, Integer, VARCHAR, Boolean, Date, ForeignKey
from datetime import datetime
from .base import Base

class SubcategoriaModel(Base):
  __tablename__ = "subcategoria"
  id_subcat = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
  nombre = Column(VARCHAR(255), nullable=True)
  observacion = Column(VARCHAR(255), nullable=True)
  fecha_creacion = Column(Date, default=datetime.now, nullable=False)
  fecha_modificacion = Column(Date, default=datetime.now, onupdate=datetime.now, nullable=True)
  estado = Column(Boolean, default=True, nullable=True)
  id_categoria = Column(Integer, ForeignKey("categoria.id_categoria"), nullable=True)

  # Relación con la tabla de elementos especificos
  id_elemespec = Column(Integer, ForeignKey("elemento_especifico.id_elemespec"), nullable=True)

  # Relación con la tabla de porcentaje de utilidad
  id_porcentaje_utilidad = Column(Integer, ForeignKey("porcentaje_utilidad.id_porcentaje_utilidad"), nullable=True)