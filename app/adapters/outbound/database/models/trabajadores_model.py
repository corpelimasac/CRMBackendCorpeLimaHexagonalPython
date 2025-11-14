from datetime import datetime

from sqlalchemy import Column, Integer, String, Date, Enum, DECIMAL

from .base import Base


class TrabajadoresModel(Base):
    """
    Modelo SQLAlchemy para la tabla de trabajadores

    Esta clase representa la tabla 'trabajadores' en la base de datos.
    Contiene la información personal y laboral de los trabajadores.
    """
    __tablename__ = "trabajadores"

    id_trabajador = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    cargo = Column(String(100), nullable=False)
    celular = Column(Integer, nullable=True, unique=True)
    sueldo = Column(DECIMAL(10, 2), nullable=False)
    porcentaje_pension = Column(DECIMAL(5, 2), nullable=False)
    tipo_contrato = Column(Enum('AMBOS', 'PLANILLA', 'RH'), nullable=False)
    tipo_entidad_pension = Column(Enum('AFP', 'ONP'), nullable=True)
    estado = Column(Integer, nullable=False, default=1)  # BIT(1) se mapea a Integer
    fecha_creacion = Column(Date, nullable=False, default=datetime.now)
    fecha_modificacion = Column(Date, nullable=True, onupdate=datetime.now)
