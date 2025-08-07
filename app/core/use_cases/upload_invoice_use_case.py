from app.core.ports.services.invoice_processor_port import InvoiceProcessorPort
from app.core.ports.services.file_storage_port import FileStoragePort
import os

class UploadInvoiceUseCase:
  """Caso de uso para subir un XML"""
  def __init__(self, invoice_processor: InvoiceProcessorPort, file_storage: FileStoragePort, files_dir: str):
    self.invoice_processor = invoice_processor
    self.file_storage = file_storage
    self.files_dir = files_dir

  async def execute(self, xml_content: bytes, original_filename: str) -> tuple[bytes, str]:
        """Orquesta el proceso de guardar, procesar y limpiar."""
        temp_path = None
        pdf_path = None
        try:
            
            # Crear carpeta files si no existe
            os.makedirs(self.files_dir, exist_ok=True)

            # 1. Usar el puerto de almacenamiento para guardar
            temp_path = await self.file_storage.save(xml_content, original_filename)
            
            # 2. Usar el puerto de procesamiento para convertir a PDF
            pdf_bytes, pdf_filename = self.invoice_processor.process_to_pdf(temp_path)

            pdf_path=os.path.join(self.files_dir, pdf_filename)

            print(f"PDF guardado en: {pdf_path}")
            
            return pdf_bytes, pdf_filename
        finally:
            # 3. Usar el puerto de almacenamiento para limpiar
            if temp_path:
                await self.file_storage.cleanup(temp_path)

            #4. Eliminar PDF temporal
            if pdf_path:
                await self.file_storage.cleanup_pdf(pdf_path)