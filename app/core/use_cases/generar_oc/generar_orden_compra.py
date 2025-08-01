from app.core.domain.entities.ordenes_compra import OrdenesCompra # ... y otros
from app.core.ports.repositories.ordenes_compra_repository import OrdenesCompraRepositoryPort
from app.core.ports.repositories.cotizacion_repository import CotizacionRepositoryPort
from app.core.ports.repositories.cotizaciones_versiones_repository import CotizacionVersionRepositoryPort
from app.core.ports.services.generator_excel_port import ExcelGeneratorPort
from app.core.ports.services.file_storage_port import FileStoragePort
from app.adapters.inbound.api.schemas.ordenes_compra_schemas import OrdenesCompraRequest
from typing import List

class GenerarOrdenCompra:   
    def __init__(
        self,
        ordenes_compra_repo: OrdenesCompraRepositoryPort,
        cotizacion_repo: CotizacionRepositoryPort,
        cotizacion_version_repo: CotizacionVersionRepositoryPort,
        excel_generator: ExcelGeneratorPort,
        file_storage: FileStoragePort
    ):
        self.ordenes_compra_repo = ordenes_compra_repo
        self.cotizacion_repo = cotizacion_repo
        self.cotizacion_version_repo = cotizacion_version_repo
        self.excel_generator = excel_generator
        self.file_storage = file_storage

    def execute(self, request: OrdenesCompraRequest) -> List[str]:

        if not self.cotizacion_repo.exists_by_id(request.idCotizacion):
            raise ValueError("La cotización especificada no existe.")

        if not self.cotizacion_version_repo.exists_by_id(request.idVersion):
            raise ValueError("La versión de cotización especificada no existe.")

        generated_files_urls = []
        for order_data in request.data:
            # 2. Mapear DTO a Entidad de Dominio
            ordenes_compra_entity = OrdenesCompra(...) # Crear la entidad con los datos

            # 3. Guardar en la base de datos (usando el puerto de OC)
            saved_order = self.ordenes_compra_repo.save(ordenes_compra_entity)

            print(saved_order)
            
            # 4. Generar el Excel (usando el puerto de Excel)
            #excel_bytes = self.excel_generator.generate_for_order(saved_order)
            
            # 5. Guardar en S3 (usando el puerto de almacenamiento)
            #filename = f"OC-{saved_order.id_proveedor}-{saved_order.id_cotizacion}.xlsx"
            #file_url = self.file_storage.save(excel_bytes, filename)
            
            #generated_files_urls.append(file_url)

        return generated_files_urls