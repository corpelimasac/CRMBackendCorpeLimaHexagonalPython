import os
from app.core.ports.services.file_storage_port import FileStoragePort
from typing import List

class LocalFileStorageAdapter(FileStoragePort):
    def __init__(self, base_dir: str = "./temp_files"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    async def save(self, file_content: bytes, filename: str) -> str:
        path = os.path.join(self.base_dir, filename)
        with open(path, "wb") as f:
            f.write(file_content)
        return path

    async def save_multiple(self, files: dict[str, bytes]) -> List[str]:
        """Guarda múltiples archivos localmente y devuelve lista de rutas"""
        paths = []
        for filename, content in files.items():
            path = await self.save(content, filename)
            paths.append(path)
        return paths

    async def cleanup(self, file_path: str):
        if os.path.exists(file_path):
            os.remove(file_path)

    async def cleanup_pdf(self, file_path: str):
        if os.path.exists(file_path):
            os.remove(file_path)
            

    async def saveS3(self, file_content:bytes, filename:str) -> str:
        pass

    