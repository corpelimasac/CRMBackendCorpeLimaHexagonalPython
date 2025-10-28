from abc import ABC, abstractmethod
from typing import List

class FileStoragePort(ABC):
  """Puerto para intractucar con un sistema de almacenamiento de archivos"""
  @abstractmethod
  async def save(self, file_content:bytes, filename:str) -> str:
    """Guarda un archivo y devuelve su ruta o ID"""
    pass #Indica que el metodo no tiene implementacion

  @abstractmethod
  async def save_multiple(self, files: dict[str, bytes]) -> List[str]:
    """Guarda múltiples archivos y devuelve lista de URLs"""
    pass

  @abstractmethod
  async def cleanup(self, filename:str) :
    """Elimina un archivo temporal"""
    pass

  @abstractmethod
  async def cleanup_pdf(self, filename:str) :
    """Elimina un archivo temporal PDF"""
    pass
