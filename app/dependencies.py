from app.adapters.outbound.storage.local_file_storage import LocalFileStorageAdapter
from app.adapters.outbound.invoice.xml_to_pdf_processor import XmlToPdfProcessorAdapter
from app.core.use_cases.end_quotation.get_finalized_quotation_use_case import GetFinalizedQuotationUseCase
from app.adapters.outbound.database.repositories.productos_cotizaciones_repository import ProductosCotizacionesRepository
from app.config.database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session

    
# 2. Importar el Caso de Uso del core
from app.core.use_cases.upload_invoice_use_case import UploadInvoiceUseCase

# --- Creación de Instancias (Singletons para eficiencia) ---

# Se crea una única instancia de cada adaptador para reutilizarla
storage_adapter = LocalFileStorageAdapter()
processor_adapter = XmlToPdfProcessorAdapter()
files_dir = "./app/shared/serializers/pdf_generator/files"

# Inyección de dependencias para las cartas de garantia

def get_upload_invoice_use_case() -> UploadInvoiceUseCase:
    """
    Construye y devuelve una instancia del caso de uso con sus dependencias ya "inyectadas".
    """
    # Aquí ocurre la inyección: pasamos las instancias concretas al constructor
    use_case_instance = UploadInvoiceUseCase(
        file_storage=storage_adapter,
        invoice_processor=processor_adapter,
        files_dir=files_dir
    )
    return use_case_instance

# Inyección de dependencias para la cotización finalizada
def get_finalized_quotation_use_case(db: Session = Depends(get_db)) -> GetFinalizedQuotationUseCase:
    """
    Construye y devuelve una instancia del caso de uso de cotización finalizada con sus dependencias inyectadas.
    """
    productos_cotizaciones_repo = ProductosCotizacionesRepository(db)
    return GetFinalizedQuotationUseCase(productos_cotizaciones_repo=productos_cotizaciones_repo)