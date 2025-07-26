from app.core.ports.services.invoice_processor_port import InvoiceProcessorPort
from app.core.ports.services.file_storage_port import FileStoragePort


class UploadInvoiceUseCase:
  """Caso de uso para subir una factura XML"""
  def __init__(self, invoice_processor: InvoiceProcessorPort, file_storage: FileStoragePort):
    self.invoice_processor = invoice_processor
    self.file_storage = file_storage

  async def execute(self, xml_content: bytes, original_filename: str) -> tuple[bytes, str]:
        """Orquesta el proceso de guardar, procesar y limpiar."""
        temp_path = None
        try:
            # 1. Usar el puerto de almacenamiento para guardar
            temp_path = await self.storage.save(xml_content, original_filename)
            
            # 2. Usar el puerto de procesamiento para convertir a PDF
            pdf_bytes, pdf_filename = self.processor.process_to_pdf(temp_path)
            
            return pdf_bytes, pdf_filename
        finally:
            # 3. Usar el puerto de almacenamiento para limpiar
            if temp_path:
                await self.storage.cleanup(temp_path)