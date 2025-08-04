from app.adapters.outbound.storage.local_file_storage import LocalFileStorageAdapter
from app.adapters.outbound.storage.aws_file_storage import AWSFileStorage
from app.adapters.outbound.invoice.xml_to_pdf_processor import XmlToPdfProcessorAdapter
from app.core.use_cases.end_quotation.get_finalized_quotation_use_case import GetFinalizedQuotationUseCase
from app.adapters.outbound.database.repositories.productos_cotizaciones_repository import ProductosCotizacionesRepository
from app.config.database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session

    
# 2. Importar el Caso de Uso del core
from app.core.use_cases.upload_invoice_use_case import UploadInvoiceUseCase
from app.core.use_cases.proveedores.get_provider_contacts_use_case import GetProviderContactsUseCase
from app.adapters.outbound.database.repositories.proveedores_repository import ProveedoresRepository
from app.core.use_cases.generar_oc.generar_orden_compra import GenerarOrdenCompra
from app.adapters.outbound.database.repositories.ordenes_compra_repository1 import OrdenesCompraRepository
from app.adapters.outbound.database.repositories.cotizacion_version_repository import CotizacionVersionesRepository
from app.adapters.outbound.excel.openpyxl_excel_generator import OpenPyXLExcelGenerator

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

# Inyección de dependencias para los contactos de los proveedores
def get_provider_contacts_use_case(db: Session = Depends(get_db)) -> GetProviderContactsUseCase:
    provider_repo = ProveedoresRepository(db)
    return GetProviderContactsUseCase(provider_repo=provider_repo)

# Inyección de dependencias para la generación de ordenes de compra
def get_generate_purchase_order_use_case(db: Session = Depends(get_db)) -> GenerarOrdenCompra:
    print("Iniciando inyección de dependencias")
    ordenes_compra_repo = OrdenesCompraRepository(db)
    return GenerarOrdenCompra(
       ordenes_compra_repo=ordenes_compra_repo,
       cotizacion_version_repo=CotizacionVersionesRepository(db),
       excel_generator=OpenPyXLExcelGenerator(ordenes_compra_repo),    
       file_storage=AWSFileStorage()
    )
    