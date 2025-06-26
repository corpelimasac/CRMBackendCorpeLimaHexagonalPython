from sqlalchemy import Column, Integer, VARCHAR, Boolean, Date, ForeignKey
from datetime import datetime
from .base import Base

class ElementoEspecificoModel(Base):
  __tablename__ = "elemento_especifico"
  id_elemespec = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
  nombre = Column(VARCHAR(255), nullable=True)
  observacion = Column(VARCHAR(255), nullable=True)
  fecha_creacion = Column(Date, default=datetime.now, nullable=False)
  fecha_modificacion = Column(Date, default=datetime.now, onupdate=datetime.now, nullable=True)
  estado = Column(Boolean, default=True, nullable=True)

  # Relación con la tabla de subcategorias
  id_subcat = Column(Integer, ForeignKey("subcategoria.id_subcat"), nullable=True)

  # Relación con la tabla de porcentaje de utilidad
  id_porcentaje_utilidad = Column(Integer, ForeignKey("porcentaje_utilidad.id_porcentaje_utilidad"), nullable=True)