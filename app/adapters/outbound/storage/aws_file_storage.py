from app.core.ports.services.file_storage_port import FileStoragePort
from app.adapters.outbound.external_services.aws.s3_service import S3Service
from app.config.settings import get_settings
import os
import tempfile
from typing import List
import re
import unicodedata


def _normalize_filename(filename: str) -> str:
    """
    Normaliza el nombre del archivo para que sea seguro en URLs de S3:
    - Elimina espacios al inicio y al final
    - Elimina diacríticos (tildes) y convierte ñ/Ñ -> n/N
    - Reemplaza espacios y guiones bajos por guiones medios (-)
    - Reemplaza caracteres no seguros por guiones medios (-)
    - Colapsa guiones consecutivos y convierte el nombre (sin extensión) a MAYÚSCULAS
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

    # 1) Quitar diacríticos (e.g., "á" -> "a", "ñ" -> "n")
    name = unicodedata.normalize('NFKD', name)
    name = ''.join(c for c in name if not unicodedata.combining(c))

    # 2) Reemplazar espacios por guiones (colapsando múltiples)
    name = re.sub(r'\s+', '-', name)
    #    Reemplazar guiones bajos existentes por guiones
    name = name.replace('_', '-')

    # 3) Reemplazar cualquier caracter no seguro por "-"
    #    Permitidos: letras, números, punto y guion
    name = re.sub(r'[^A-Za-z0-9.-]', '-', name)

    # 4) Colapsar guiones repetidos
    name = re.sub(r'-+', '-', name)

    # 5) Convertir a MAYÚSCULAS (solo el nombre, no la extensión)
    name = name.upper()

    # Reconstruir el nombre con extensión
    return f"{name}.{ext}" if ext else name


class AWSFileStorage(FileStoragePort):
    def __init__(self):
        settings = get_settings()
        self.bucket_name = settings.aws_bucket_name
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
