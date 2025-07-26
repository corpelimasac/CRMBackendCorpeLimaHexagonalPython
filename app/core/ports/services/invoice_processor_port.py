from abc import ABC, abstractmethod

class InvoiceProcessorPort(ABC):
  """Puerto para procesar un XML y convertira a otro formato PDF"""
  @abstractmethod
  def process_to_pdf(self, xml_file_path: str) -> tuple[bytes, str]:
    """Procesa un archivo XML y devuelve el contenido del PDF y su nombre."""
    pass

