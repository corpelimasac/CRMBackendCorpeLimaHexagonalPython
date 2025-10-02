"""
Servicio de caché con Redis
"""
import redis
import json
import os
from typing import Optional, Dict, Any
from datetime import timedelta
class RedisCacheService:
  """
  Servicio para manejar el caché de datos con Redis
  """
  def __init__(self) :
    """
    Inicializa la conexión a redis"""
    # Obtiene la URL de Redis desde variables de entorno
    # Por defecto: redis://localhost:6379 (desarrollo local)
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')

    try:
      self.client=redis.from_url(
        redis_url,
        decode_responses=True,   ##Convierte a bytes a strings automaticamente
        socket_connect_timeout=5,
        socket_timeout=5

      )
      self.client.ping()
      print(f"✅ Conectado a Redis: {redis_url}")
    except redis.ConnectionError as e:
      print(f"Error conectado a Redis",e)

  def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un valor del caché

        Args:
            key: Clave del caché (ej: "sunat:ruc:20123456789")

        Returns:
            Diccionario con los datos o None si no existe
        """
        if not self.client:
            return None

        try:
            data = self.client.get(key)
            if data:
                print(f"✅ Cache HIT: {key}")
                return json.loads(data)
            else:
                print(f"❌ Cache MISS: {key}")
                return None
        except Exception as e:
            print(f"⚠️ Error obteniendo del caché: {e}")
            return None

  def set(
        self,
        key: str,
        value: Dict[str, Any],
        ttl_seconds: int = 604800  # 7 días por defecto
    ) -> bool:
        """
        Guarda un valor en el caché con tiempo de expiración

        Args:
            key: Clave del caché
            value: Diccionario con los datos a guardar
            ttl_seconds: Tiempo de vida en segundos (default: 7 días)

        Returns:
            True si se guardó correctamente, False si hubo error
        """
        if not self.client:
            return False

        try:
            serialized_value = json.dumps(value, ensure_ascii=False)
            self.client.setex(key, ttl_seconds, serialized_value)
            print(f"💾 Guardado en caché: {key} (TTL: {ttl_seconds}s)")
            return True
        except Exception as e:
            print(f"⚠️ Error guardando en caché: {e}")
            return False

  def delete(self, key: str) -> bool:
        """
        Elimina un valor del caché

        Args:
            key: Clave del caché a eliminar

        Returns:
            True si se eliminó, False si hubo error
        """
        if not self.client:
            return False

        try:
            self.client.delete(key)
            print(f"🗑️ Eliminado del caché: {key}")
            return True
        except Exception as e:
            print(f"⚠️ Error eliminando del caché: {e}")
            return False

  def clear_pattern(self, pattern: str) -> int:
        """
        Elimina todas las claves que coincidan con un patrón

        Args:
            pattern: Patrón de búsqueda (ej: "sunat:ruc:*")

        Returns:
            Número de claves eliminadas
        """
        if not self.client:
            return 0

        try:
            keys = self.client.keys(pattern)
            if keys:
                deleted = self.client.delete(*keys)
                print(f"🗑️ Eliminadas {deleted} claves con patrón: {pattern}")
                return deleted
            return 0
        except Exception as e:
            print(f"⚠️ Error limpiando caché: {e}")
            return 0

  
  def health_check(self) -> bool:
        """
        Verifica si Redis está funcionando

        Returns:
            True si Redis responde, False si no
        """
        if not self.client:
            return False

        try:
            return self.client.ping()
        except Exception:
            return False


# Singleton: Una única instancia para toda la aplicación
_cache_service = None

def get_cache_service() -> RedisCacheService:
    """
    Obtiene la instancia única del servicio de caché
    """
    global _cache_service
    if _cache_service is None:
        _cache_service = RedisCacheService()
    return _cache_service