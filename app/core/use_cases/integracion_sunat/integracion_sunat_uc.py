"""
Caso de uso para la integración con SUNAT
"""
from typing import Dict
from app.adapters.outbound.external_services.sunat.sunat_scraper import SunatScrapper
import asyncio

from app.config.cache.redis_cache import get_cache_service


def _validar_ruc(ruc: str) -> bool:
    """
    Valida el formato del RUC

    Args:
        ruc (str): Número de RUC a validar

    Returns:
        bool: True si el formato es válido
    """
    # El RUC debe tener exactamente 11 dígitos
    if not ruc or len(ruc) != 11:
        return False

    # Debe contener solo números
    if not ruc.isdigit():
        return False

    return True


class IntegracionSunatUC:
    """
    Caso de uso para consultar información de RUC en SUNAT
    """

    def __init__(self, sunat_scraper: SunatScrapper):
        self.sunat_scraper = sunat_scraper
        self.cache_service = get_cache_service()
        self.cache_ttl = 604800  # 7 días en segundos

    async def obtener_ruc(self, ruc: str) -> Dict:
        """
        Obtiene información de un RUC desde SUNAT

        Args:
            ruc (str): Número de RUC a consultar

        Returns:
            Dict: Información del RUC o mensaje de error
        """
        # Validar formato de RUC
        if not _validar_ruc(ruc):
            return {
                "message": "Error al consultar RUC",
                "detail": "El formato del RUC no es válido. Debe tener 11 dígitos.",
                "ruc": ruc
            }

        # 1. BUSCAR EN CACHÉ PRIMERO
        cache_key = f"sunat:ruc:{ruc}"
        cached_data = self.cache_service.get(cache_key)

        if cached_data:
            print(f"Retornando datos desde cache para RUC: {ruc}")
            return cached_data

        # 2. NO ESTÁ EN CACHÉ, CONSULTAR SUNAT
        print(f"RUC {ruc} no encontrado en cache, consultando SUNAT...")

        try:
            # Ejecutar consulta síncrona de Playwright sin bloquear el event loop
            resultado = await asyncio.to_thread(self.sunat_scraper.consultar_ruc, ruc)

            # 3. VERIFICAR SI HUBO ERROR EN LA CONSULTA
            if resultado.get("razonSocial") == "Error en consulta":
                error_msg = resultado.get("error", "Error desconocido")
                print(f"Error al consultar RUC {ruc}: {error_msg}")
                return {
                    "message": "Error al consultar RUC",
                    "detail": f"No se pudo obtener información del RUC {ruc}. Error: {error_msg}",
                    "ruc": ruc
                }

            # 4. CONSULTA EXITOSA, GUARDAR EN CACHÉ
            print(f"Consulta exitosa para RUC: {ruc}")
            self.cache_service.set(cache_key, resultado, self.cache_ttl)

            return resultado

        except Exception as e:
            print(f"Error inesperado al consultar RUC {ruc}: {str(e)}")
            return {
                "message": "Error al consultar RUC",
                "detail": f"Error interno al consultar el RUC {ruc}: {str(e)}",
                "ruc": ruc
            }
