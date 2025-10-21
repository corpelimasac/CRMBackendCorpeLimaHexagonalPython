from app.core.ports.services.file_storage_port import FileStoragePort
from app.adapters.outbound.external_services.aws.s3_service import S3Service
from app.config.settings import get_settings
import os
import tempfile
from typing import List
import re


def _normalize_filename(filename: str) -> str:
    """
    Normaliza el nombre del archivo para que sea seguro en URLs de S3:
    - Elimina espacios al inicio y al final
    - Reemplaza espacios múltiples internos por un solo guión bajo
    - Reemplaza espacios simples por guiones bajos
    """
    # Separar nombre y extensión
    name_parts = filename.rsplit('.', 1)
    if len(name_parts) == 2:
        name, ext = name_parts
    else:
        name = filename
        ext = ''

    # Normalizar el nombre (sin extensión)
    name = name.strip()  # Eliminar espacios inicio/final
    name = re.sub(r'\s+', '_', name)  # Reemplazar espacios múltiples por un guión bajo

    # Reconstruir el nombre con extensión
    return f"{name}.{ext}" if ext else name


class AWSFileStorage(FileStoragePort):
    def __init__(self):
        settings = get_settings()
        self.bucket_name = settings.s3_bucket_name
        self.region = settings.aws_region
        self.s3_service = S3Service()

    async def save(self, file_content: bytes, filename: str) -> str:
        """Guarda un archivo en S3 y devuelve su URL"""
        # Normalizar el nombre del archivo para evitar problemas con espacios en URLs
        filename = _normalize_filename(filename)

        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        try:
            # Subir a S3 usando S3Service
            s3_key = f"ordenes_de_compra/{filename}"
            url = self.s3_service.upload_file(temp_file_path, s3_key, self.bucket_name, self.region)
            return url
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    async def save_s3(self, file_content: bytes, filename: str) -> str:
        """Guarda un archivo en S3 y devuelve su URL (implementación del método abstracto)"""
        return await self.save(file_content, filename)

    async def save_multiple(self, files: dict[str, bytes]) -> List[str]:
        """Guarda múltiples archivos en S3 y devuelve lista de URLs"""
        urls = []
        for filename, content in files.items():
            url = await self.save(content, filename)
            urls.append(url)
        return urls

    async def cleanup(self, filename: str):
        """Elimina un archivo temporal (no aplicable para S3)"""
        pass

    async def cleanup_pdf(self, filename: str):
        """Elimina un archivo temporal PDF (no aplicable para S3)"""
        pass
