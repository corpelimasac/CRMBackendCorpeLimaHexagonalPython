from sqlalchemy import Column, Integer, VARCHAR, Boolean, Date
from datetime import datetime
from .base import Base

class MarcasModel(Base):
  __tablename__ = "marcas"
  id_marca = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
  nombre = Column(VARCHAR(100), nullable=True)
  estado = Column(Boolean, default=True, nullable=True)
  fecha_creacion = Column(Date, default=datetime.now, nullable=False)
  fecha_modificacion = Column(Date, default=datetime.now, onupdate=datetime.now, nullable=True)
  observacion = Column(VARCHAR(255), nullable=True)