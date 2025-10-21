import boto3
from typing import Optional
from botocore.exceptions import ClientError
from urllib.parse import unquote
import logging

from app.config.settings import get_settings

logger = logging.getLogger(__name__)


def _extract_key_from_url(s3_url: str, bucket: str) -> Optional[str]:
    """
    Extrae la clave (key) del archivo desde una URL de S3.
    Maneja URLs con espacios (archivos antiguos) y con guiones bajos (archivos nuevos).

    Args:
        s3_url (str): URL completa del archivo en S3
        bucket (str): Nombre del bucket

    Returns:
        Optional[str]: La clave del archivo o None si no se pudo extraer
    """
    try:
        # Formato esperado: https://bucket.s3.region.amazonaws.com/path/to/file
        # o https://s3.region.amazonaws.com/bucket/path/to/file

        # Primero, aplicar URL decode a toda la URL para manejar %20 y otros caracteres codificados
        s3_url_decoded = unquote(s3_url)

        # Eliminar el protocolo
        url_without_protocol = s3_url_decoded.replace("https://", "").replace("http://", "")

        # Caso 1: bucket.s3.region.amazonaws.com/key
        if url_without_protocol.startswith(f"{bucket}.s3."):
            parts = url_without_protocol.split("/", 1)
            if len(parts) > 1:
                key = parts[1]
                logger.info(f"Key extraída de URL: '{key}'")
                return key

        # Caso 2: s3.region.amazonaws.com/bucket/key
        elif "s3." in url_without_protocol and url_without_protocol.startswith("s3."):
            parts = url_without_protocol.split("/")
            if len(parts) > 2 and parts[1] == bucket:
                key = "/".join(parts[2:])
                logger.info(f"Key extraída de URL: '{key}'")
                return key

        logger.warning(f"No se pudo extraer key de la URL. URL procesada: {url_without_protocol}")
        return None
    except Exception as e:
        logger.error(f"Error al extraer clave de URL: {e}")
        return None

class S3Service:
    """
    Servicio genérico para operaciones con AWS S3.
    Proporciona métodos reutilizables para subir, eliminar y gestionar archivos en S3.
    """

    def __init__(self):
        """
        Inicializa el cliente de S3 con las credenciales del entorno.
        """
        settings = get_settings()
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )

    def upload_file(self, local_path: str, s3_key: str, bucket: str, region: str) -> str:
        """
        Sube un archivo a S3 y retorna la URL pública.

        Args:
            local_path (str): Ruta local del archivo a subir
            s3_key (str): Clave del archivo en S3
            bucket (str): Nombre del bucket
            region (str): Región de AWS

        Returns:
            str: URL pública del archivo en S3

        Raises:
            ClientError: Si hay un error al subir el archivo
        """
        try:
            self.s3_client.upload_file(
                local_path,
                bucket,
                s3_key,
                ExtraArgs={'ACL': 'public-read'}
            )
            url = f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"
            logger.info(f"Archivo subido exitosamente a S3: {url}")
            return url
        except ClientError as e:
            logger.error(f"Error al subir archivo a S3: {e}")
            raise

    def delete_file(self, s3_key: str, bucket: str) -> bool:
        """
        Elimina un archivo de S3 usando la clave del archivo.
        Intenta eliminar con la key original y, si falla, con versiones normalizadas.

        Args:
            s3_key (str): Clave del archivo en S3 (path dentro del bucket)
            bucket (str): Nombre del bucket

        Returns:
            bool: True si se eliminó exitosamente, False en caso contrario

        Raises:
            ClientError: Si hay un error al eliminar el archivo
        """
        try:
            # Intentar eliminar con la key original
            self.s3_client.delete_object(Bucket=bucket, Key=s3_key)
            logger.info(f"Archivo eliminado exitosamente de S3: {s3_key} del bucket {bucket}")
            return True
        except ClientError as e:
            # Si falla, intentar con versión normalizada (espacios por guiones bajos)
            if ' ' in s3_key:
                try:
                    s3_key_normalized = s3_key.replace(' ', '_')
                    logger.info(f"Intentando eliminar con key normalizada: {s3_key_normalized}")
                    self.s3_client.delete_object(Bucket=bucket, Key=s3_key_normalized)
                    logger.info(f"Archivo eliminado con key normalizada: {s3_key_normalized}")
                    return True
                except ClientError as e2:
                    logger.error(f"Error al eliminar archivo con key normalizada: {e2}")

            logger.error(f"Error al eliminar archivo de S3: {e}")
            raise

    def delete_file_from_url(self, s3_url: str, bucket: str) -> bool:
        """
        Elimina un archivo de S3 extrayendo la clave desde la URL completa.

        Args:
            s3_url (str): URL completa del archivo en S3
                         (ej: https://bucket.s3.region.amazonaws.com/path/to/file.xlsx)
            bucket (str): Nombre del bucket

        Returns:
            bool: True si se eliminó exitosamente, False en caso contrario

        Raises:
            ValueError: Si la URL no es válida
            ClientError: Si hay un error al eliminar el archivo
        """
        try:
            # Extraer la clave (key) de la URL
            s3_key = _extract_key_from_url(s3_url, bucket)

            if not s3_key:
                raise ValueError(f"No se pudo extraer la clave de la URL: {s3_url}")

            return self.delete_file(s3_key, bucket)
        except Exception as e:
            logger.error(f"Error al eliminar archivo desde URL {s3_url}: {e}")
            raise

    def file_exists(self, s3_key: str, bucket: str) -> bool:
        """
        Verifica si un archivo existe en S3.

        Args:
            s3_key (str): Clave del archivo en S3
            bucket (str): Nombre del bucket

        Returns:
            bool: True si el archivo existe, False en caso contrario
        """
        try:
            self.s3_client.head_object(Bucket=bucket, Key=s3_key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                logger.error(f"Error al verificar existencia del archivo: {e}")
                raise
