from app.core.ports.services.file_storage_port import FileStoragePort
from app.adapters.outbound.external_services.aws.upload_file_to_s3 import upload_file_to_s3
import os
import tempfile
from typing import List

class AWSFileStorage(FileStoragePort):
    def __init__(self, bucket_name: str = 'bucketcorpe', region: str = 'us-east-1'):
        self.bucket_name = bucket_name
        self.region = region

    async def save(self, file_content: bytes, filename: str) -> str:
        """Guarda un archivo en S3 y devuelve su URL"""
        # Debug: Verificar credenciales AWS
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY') 
        print(f"DEBUG AWS - Access Key ID disponible: {'Sí' if aws_access_key else 'No'}")
        print(f"DEBUG AWS - Secret Key disponible: {'Sí' if aws_secret_key else 'No'}")
        if aws_access_key:
            print(f"DEBUG AWS - Access Key ID (primeros 8 chars): {aws_access_key[:8]}...")
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        try:
            # Subir a S3
            s3_key = f"ordenes_de_compra/{filename}"
            print(f"DEBUG AWS - Intentando subir a S3: {s3_key}")
            url = upload_file_to_s3(temp_file_path, s3_key, self.bucket_name, self.region)
            return url
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    async def saveS3(self, file_content: bytes, filename: str) -> str:
        """Alias para save - guarda un archivo en S3 y devuelve su URL"""
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