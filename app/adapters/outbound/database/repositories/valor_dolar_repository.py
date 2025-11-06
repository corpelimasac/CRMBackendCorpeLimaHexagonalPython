"""
Repositorio para el valor del dólar
"""
from sqlalchemy.orm import Session
from typing import Optional
from app.adapters.outbound.database.models.value_dolar_model import ValueDolarModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ValorDolarRepository:
    """
    Repositorio para manejar las operaciones de base de datos relacionadas con el valor del dólar.
    """
    
    def __init__(self, db: Session):
        self.db = db

    def create_valor_dolar(self, valor_dolar_data: dict) -> Optional[ValueDolarModel]:
        """
        Crea un nuevo registro del valor del dólar en la base de datos a partir de un diccionario.
        """
        try:
            # Prepara una copia de los datos para no modificar el diccionario original
            data_to_insert = valor_dolar_data.copy()

            # Convierte la fecha de string a objeto datetime si es necesario
            if 'fecha' in data_to_insert and isinstance(data_to_insert['fecha'], str):
                data_to_insert['fecha'] = datetime.strptime(data_to_insert['fecha'], '%d-%m-%Y %H:%M')

            nuevo_valor = ValueDolarModel(**data_to_insert)
            self.db.add(nuevo_valor)
            self.db.commit()
            self.db.refresh(nuevo_valor)
            logger.info("Valor del dólar insertado correctamente")
            return nuevo_valor
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al insertar valor del dólar: {e}")
            return None

    def fetch_last_value_dolar(self) -> Optional[ValueDolarModel]:
        """Obtener el último valor insertado en la tabla usando SQLAlchemy ORM."""
        try:
            return self.db.query(ValueDolarModel).order_by(ValueDolarModel.id_dolar.desc()).first()
        except Exception as e:
            logger.error(f"Error al consultar el último valor del dólar: {e}")
            return None 
