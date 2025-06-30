from sqlalchemy import Column, Integer, Float, DateTime
from app.adapters.outbound.database.models.base import Base

class ValueDolarModel(Base):
    __tablename__ = "value_dolar"
    id_dolar = Column(Integer, primary_key=True, autoincrement=True)
    venta = Column(Float)
    compra = Column(Float)
    fecha = Column(DateTime)
