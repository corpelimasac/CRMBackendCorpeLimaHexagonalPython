"""
Caso de uso para la integración con SUNAT
"""
from typing import Dict
from app.adapters.outbound.external_services.sunat.sunat_scraper import SunatScraper
import re
import asyncio
from selenium.common.exceptions import TimeoutException


class IntegracionSunatUC:
    """
    Caso de uso para consultar información de RUC en SUNAT
    """
    
    def __init__(self, sunat_scraper: SunatScraper):
        self.sunat_scraper = sunat_scraper

    async def obtener_ruc(self, ruc: str, max_intentos: int = 3) -> Dict:
        """
        Obtiene información de un RUC desde SUNAT con mecanismo de reintentos
        
        Args:
            ruc (str): Número de RUC a consultar
            max_intentos (int): Número máximo de intentos
            
        Returns:
            Dict: Información del RUC o error
        """
        # Validar formato de RUC
        if not self._validar_ruc(ruc):
            return {
                "message": "Error al consultar RUC",
                "detail": "El formato del RUC no es válido. Debe tener 11 dígitos.",
                "ruc": ruc
            }
        
        ultimo_error = None
        
        for intento in range(1, max_intentos + 1):
            try:
                print(f"Intento {intento}/{max_intentos} para RUC {ruc}")

                # Realizar consulta en SUNAT con modo rápido por defecto
                resultado = self.sunat_scraper.consultar_ruc(ruc, modo_rapido=True)

                # Verificar si hubo error en la consulta
                if "error" in resultado and resultado["razonSocial"] == "Error en consulta":
                    ultimo_error = resultado.get('error', 'Error desconocido')

                    # Verificar si es un error de timeout para recrear el driver
                    if "timeout" in ultimo_error.lower() or "timed out" in ultimo_error.lower():
                        print(f"Timeout detectado, recreando WebDriver...")
                        self.sunat_scraper.driver_manager.cleanup()
                        await asyncio.sleep(2)  # Pausa más larga para timeouts

                    if intento < max_intentos:
                        print(f"Error en intento {intento}, reintentando...")
                        continue
                    else:
                        return {
                            "message": "Error al consultar RUC",
                            "detail": f"No se pudo obtener información del RUC {ruc} después de {max_intentos} intentos. Último error: {ultimo_error}",
                            "ruc": ruc
                        }

                # Si llegamos aquí, la consulta fue exitosa
                print(f"Consulta exitosa en intento {intento}")
                return resultado

            except TimeoutException as e:
                ultimo_error = f"Timeout del WebDriver: {str(e)}"
                print(f"Timeout en intento {intento}: {ultimo_error}")

                # Para errores de timeout, limpiar el driver y reintentar
                print("Recreando WebDriver debido a timeout...")
                self.sunat_scraper.driver_manager.cleanup()

                if intento < max_intentos:
                    print(f"Reintentando en 3 segundos...")
                    await asyncio.sleep(3)
                    continue

            except Exception as e:
                ultimo_error = str(e)
                print(f"Error en intento {intento}: {ultimo_error}")

                # Verificar si el error contiene indicios de timeout
                if "timeout" in ultimo_error.lower() or "timed out" in ultimo_error.lower():
                    print("Error relacionado con timeout, recreando WebDriver...")
                    self.sunat_scraper.driver_manager.cleanup()
                    await asyncio.sleep(2)
                elif "renderer" in ultimo_error.lower():
                    print("Error del renderer, recreando WebDriver...")
                    self.sunat_scraper.driver_manager.cleanup()
                    await asyncio.sleep(2)

                if intento < max_intentos:
                    print(f"Reintentando en 2 segundos...")
                    await asyncio.sleep(2)
                    continue
        
        # Si llegamos aquí, todos los intentos fallaron
        return {
            "message": "Error al consultar RUC",
            "detail": f"Error interno al consultar el RUC {ruc} después de {max_intentos} intentos. Último error: {ultimo_error}",
            "ruc": ruc
        }

    def _validar_ruc(self, ruc: str) -> bool:
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
