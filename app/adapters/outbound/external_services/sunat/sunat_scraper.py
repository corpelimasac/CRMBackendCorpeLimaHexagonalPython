"""
Servicio de web scraping para consultar información de RUC en SUNAT
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from typing import Dict, Optional
import logging
import concurrent.futures
import threading
from queue import Queue
from datetime import datetime, timedelta
import atexit
import pandas as pd
import pickle
import os
import threading
from typing import Dict, Optional, Any # Nuevo import para tipos
# Agrega esta línea al inicio de tu archivo, después de los imports
logging.getLogger('webdriver_manager').setLevel(logging.ERROR)

# Obtener el directorio donde está ubicado este archivo
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NOMBRE_CSV = os.path.join(SCRIPT_DIR, 'ubigeo_distritos.csv')
NOMBRE_PICKLE = os.path.join(SCRIPT_DIR, 'ubigeo_map.pkl') 

class WebDriverManager:
    """
    Singleton para manejar una única instancia de WebDriver que se mantiene activa por 12 horas
    """
    _instance = None
    _lock = threading.Lock()
    _driver = None
    _created_at = None
    _max_lifetime_hours = 12
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(WebDriverManager, cls).__new__(cls)
                    # Registrar función de limpieza al salir
                    atexit.register(cls._cleanup)
        return cls._instance
    
    def get_driver(self):
        """Obtiene el WebDriver, creándolo si es necesario o si ha expirado"""
        with self._lock:
            # Verificar si el driver existe y no ha expirado
            if self._driver is not None and not self._is_expired():
                print("✅ Usando WebDriver existente...")
                return self._driver
            
            # Si el driver existe pero ha expirado, cerrarlo
            if self._driver is not None:
                print("🔄 WebDriver expirado, cerrando y creando nueva instancia...")
                self._cleanup()
            
            # Crear nueva instancia
            print("🚀 Creando nueva instancia de WebDriver (válida por 12 horas)...")
            self._driver = self._create_driver()
            self._created_at = datetime.now()
            return self._driver
    
    def _is_expired(self):
        """Verifica si el WebDriver ha expirado (más de 12 horas)"""
        if self._created_at is None:
            return True
        
        elapsed = datetime.now() - self._created_at
        return elapsed.total_seconds() > (self._max_lifetime_hours * 3600)
    
    def _create_driver(self):
        """Crea una nueva instancia de WebDriver"""
        options = self._get_chrome_options()
        
        # Intentar múltiples rutas de ChromeDriver para Railway
        chromedriver_paths = [
            "/usr/bin/chromedriver",  # Ruta del Dockerfile
            "/usr/local/bin/chromedriver",  # Ruta alternativa
            "/snap/bin/chromedriver",  # Ruta snap
        ]
        
        driver = None
        for path in chromedriver_paths:
            try:
                print(f"🔍 Intentando ChromeDriver en: {path}")
                service = ChromeService(executable_path=path)
                driver = webdriver.Chrome(service=service, options=options)
                print(f"✅ ChromeDriver exitoso en: {path}")
                break
            except Exception as e:
                print(f"❌ ChromeDriver falló en {path}: {e}")
                continue
        
        # Si no se pudo crear con rutas del sistema, usar WebDriverManager como último recurso
        if driver is None:
            try:
                print("🔄 Intentando con WebDriverManager...")
                service = ChromeService(executable_path=ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                print("✅ ChromeDriver exitoso con WebDriverManager")
            except Exception as e:
                print(f"💥 Error fatal con WebDriverManager: {e}")
                raise Exception(f"No se pudo inicializar ChromeDriver: {e}")
        
        # Timeouts más estables para evitar errores
        driver.set_page_load_timeout(20)
        driver.implicitly_wait(5)
        
        return driver
    
    def _get_chrome_options(self) -> ChromeOptions:
        """Configura las opciones de Chrome para máxima velocidad en Railway"""
        options = ChromeOptions()
        
        # User-Agent optimizado para Linux
        user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        options.add_argument(f'user-agent={user_agent}')
        
        # Configuración ULTRA RÁPIDA para Railway
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-default-apps")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")
        options.add_argument("--disable-css")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor,TranslateUI")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-logging")
        options.add_argument("--disable-gpu-logging")
        options.add_argument("--log-level=3")
        options.add_argument("--silent")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Opciones adicionales para Railway
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-ipc-flooding-protection")
        options.add_argument("--disable-hang-monitor")
        options.add_argument("--disable-prompt-on-repost")
        options.add_argument("--disable-domain-reliability")
        options.add_argument("--disable-component-extensions-with-background-pages")
        options.add_argument("--metrics-recording-only")
        options.add_argument("--no-report-upload")
        
        # Optimizaciones de memoria y red
        options.add_argument("--memory-pressure-off")
        options.add_argument("--aggressive-cache-discard")
        options.add_argument("--window-size=800,600")
        options.add_argument("--page-load-strategy=eager")
        
        # Configurar prefs para velocidad máxima
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.media_stream": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.geolocation": 2,
            "profile.default_content_setting_values.plugins": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
            "profile.managed_default_content_settings.javascript": 1,
            "profile.managed_default_content_settings.cookies": 2,
            "profile.managed_default_content_settings.popups": 2,
            "profile.managed_default_content_settings.geolocation": 2,
            "profile.managed_default_content_settings.media_stream": 2,
        }
        options.add_experimental_option("prefs", prefs)
        
        # Anti-detección
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        
        return options
    
    def _cleanup(self):
        """Limpia el WebDriver"""
        if self._driver is not None:
            try:
                print("🧹 Cerrando WebDriver...")
                self._driver.quit()
            except:
                pass
            finally:
                self._driver = None
                self._created_at = None
    
    def cleanup(self):
        """Método público para limpiar el WebDriver"""
        self._cleanup()
    
    def get_status(self):
        """Obtiene el estado del WebDriver"""
        if self._driver is None:
            return "No inicializado"
        
        if self._is_expired():
            return "Expirado"
        
        elapsed = datetime.now() - self._created_at
        remaining = timedelta(hours=self._max_lifetime_hours) - elapsed
        return f"Activo (restan {remaining})"
    
    def test_chromedriver(self):
        """Prueba si ChromeDriver está funcionando correctamente"""
        try:
            options = self._get_chrome_options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            # Probar rutas del sistema primero
            chromedriver_paths = [
                "/usr/bin/chromedriver",
                "/usr/local/bin/chromedriver",
                "/snap/bin/chromedriver",
            ]
            
            for path in chromedriver_paths:
                try:
                    print(f"🧪 Probando ChromeDriver en: {path}")
                    service = ChromeService(executable_path=path)
                    test_driver = webdriver.Chrome(service=service, options=options)
                    test_driver.get("https://www.google.com")
                    title = test_driver.title
                    test_driver.quit()
                    print(f"✅ ChromeDriver funciona en {path}: {title}")
                    return True, path
                except Exception as e:
                    print(f"❌ ChromeDriver falló en {path}: {e}")
                    continue
            
            # Probar WebDriverManager como último recurso
            try:
                print("🔄 Probando WebDriverManager...")
                service = ChromeService(executable_path=ChromeDriverManager().install())
                test_driver = webdriver.Chrome(service=service, options=options)
                test_driver.get("https://www.google.com")
                title = test_driver.title
                test_driver.quit()
                print(f"✅ WebDriverManager funciona: {title}")
                return True, "WebDriverManager"
            except Exception as e:
                print(f"❌ WebDriverManager falló: {e}")
                return False, str(e)
                
        except Exception as e:
            print(f"💥 Error en test_chromedriver: {e}")
            return False, str(e)


class UbigeoMap:
    """
    Clase Singleton para cargar y mantener el mapa de Distrito -> Ubigeo
    de forma persistente (usando pickle) en memoria.
    """
    _instance = None
    _lock = threading.Lock()
    _ubigeo_map: Optional[Dict[str, Any]] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(UbigeoMap, cls).__new__(cls)
                    cls._instance._load_map() # Cargar el mapa al crear la instancia
        return cls._instance

    def _load_map(self):
        """
        Intenta cargar el mapa desde el archivo pickle. Si falla, lo regenera desde CSV.
        Esta función solo se llama UNA VEZ al inicio.
        """
        # 1. Intentar cargar desde Pickle
        if os.path.exists(NOMBRE_PICKLE):
            try:
                with open(NOMBRE_PICKLE, 'rb') as f:
                    self._ubigeo_map = pickle.load(f)
                print(f"[OK] UbigeoMap cargado desde {NOMBRE_PICKLE} (Persistencia). Total: {len(self._ubigeo_map)} distritos.")
                return
            except Exception as e:
                print(f"[ERROR] Error al cargar {NOMBRE_PICKLE}: {e}. Regenerando desde CSV.")

        # 2. Si el pickle falla, regenerar desde CSV
        print(f"[INFO] Generando UbigeoMap desde {NOMBRE_CSV} (Lento).")
        try:
            # Verificar que el archivo existe
            if not os.path.exists(NOMBRE_CSV):
                raise FileNotFoundError(f"No se encontró el archivo: {NOMBRE_CSV}")

            print(f"[INFO] Archivo CSV encontrado en: {NOMBRE_CSV}")

            # Usar encoding='utf-8-sig' para manejar el BOM automáticamente
            # El separador es coma, no punto y coma
            df = pd.read_csv(NOMBRE_CSV, sep=',', encoding='utf-8-sig')
            print(f"[INFO] CSV cargado. Filas: {len(df)}, Columnas: {list(df.columns)}")

            # Limpiar el dataframe
            df = df.dropna(subset=['Distrito', 'Ubigeo']).drop_duplicates(subset=['Distrito'])
            print(f"[INFO] Después de limpieza. Filas: {len(df)}")

            # La clave es convertir a MAYÚSCULAS para que la búsqueda sea robusta
            diccionario_ubigeo = df.set_index(
                df['Distrito'].str.strip().str.upper()
            ).to_dict()['Ubigeo']

            self._ubigeo_map = diccionario_ubigeo
            print(f"[INFO] Diccionario creado con {len(self._ubigeo_map)} distritos")

            # Guardar el diccionario como pickle para el futuro
            with open(NOMBRE_PICKLE, 'wb') as f:
                pickle.dump(diccionario_ubigeo, f)
            print(f"[OK] UbigeoMap generado y guardado en {NOMBRE_PICKLE} para persistencia.")

        except FileNotFoundError as e:
            print(f"[ERROR] El archivo CSV '{NOMBRE_CSV}' no fue encontrado.")
            print(f"[ERROR] Ruta completa: {os.path.abspath(NOMBRE_CSV)}")
            print(f"[ERROR] Directorio actual: {os.getcwd()}")
            print(f"[ERROR] Error: {e}")
            self._ubigeo_map = {} # Devolver un diccionario vacío para evitar fallos
        except Exception as e:
            print(f"[ERROR] Fallo la generacion del UbigeoMap desde CSV: {e}")
            import traceback
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            self._ubigeo_map = {}
            

    def obtener_ubigeo(self, distrito: str) -> str:
        """
        Busca el Ubigeo. Retorna el código o "Sin ubigeo" si no lo encuentra.
        """
        if not self._ubigeo_map:
            return "Sin ubigeo (Error de carga)"
            
        # Limpiar el input para que coincida con la clave del diccionario (MAYÚSCULAS)
        distrito_limpio = distrito.strip().upper() 
        
        # Búsqueda instantánea O(1)
        ubigeo = self._ubigeo_map.get(distrito_limpio)
        
        return str(ubigeo).strip() if ubigeo else "Sin ubigeo"

    def get_archivo_pickle(self):
        # Implementación mínima para satisfacer tu esqueleto original
        return NOMBRE_PICKLE

class SunatScraper:
    """
    Servicio para realizar web scraping en la página de SUNAT usando WebDriverManager singleton
    """
    
    def __init__(self):
        self.url = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/FrameCriterioBusquedaWeb.jsp"
        self.driver_manager = WebDriverManager()
        self.ubigeo_map = UbigeoMap() 
    
    def get_driver(self):
        """Obtiene el WebDriver del manager singleton"""
        return self.driver_manager.get_driver()
    
    def get_driver_status(self):
        """Obtiene el estado del WebDriver"""
        return self.driver_manager.get_status()
    
    def test_chromedriver(self):
        """Prueba si ChromeDriver está funcionando correctamente"""
        return self.driver_manager.test_chromedriver()
    
    def consultar_ruc(self, ruc_numero: str, modo_rapido: bool = True) -> Dict:
        """
        Realiza web scraping en la página de la SUNAT para obtener datos de un RUC.
        
        Args:
            ruc_numero (str): Número de RUC a consultar
            modo_rapido (bool): Si True, omite secciones lentas para máxima velocidad
            
        Returns:
            dict: Diccionario con toda la información del RUC
        """
        
        try:
            # Obtener el driver del singleton (se crea automáticamente si es necesario)
            driver = self.get_driver()
            
            # 2. Realiza la consulta usando el driver del singleton
            print(f"Consultando RUC {ruc_numero}...")
            driver.get(self.url)

            # Timeouts más estables
            ruc_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "txtRuc"))
            )

            ruc_input.clear()
            ruc_input.send_keys(ruc_numero)

            btn_consultar = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable((By.ID, "btnAceptar"))
            )
            btn_consultar.click()

            # Esperar resultados con timeout más generoso
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "list-group"))
            )



            print("Extrayendo información...")



            # Extraer información básica (siempre necesaria)
            datos_basicos = self._extraer_datos_basicos(driver)
            
            # Extraer información adicional usando PARALELISMO
            cantidad_trabajadores = "Sin datos"
            cantidad_prestadores = "Sin datos"
            representante_legal = {
                "tipoDocumento": "Sin datos",
                "nroDocumento": "Sin datos", 
                "nombre": "Sin datos",
                "cargo": "Sin datos",
                "fechaDesde": "Sin datos"
            }
            
            # Extraer trabajadores en paralelo (solo trabajadores)
            try:
                cantidad_trabajadores, cantidad_prestadores = self._extraer_cantidad_trabajadores_rapido(driver)
                print("✅ Trabajadores extraídos")
            except Exception as e:
                 print(f"❌ Error en trabajadores: {e}")
                
                # Extraer representante legal de forma síncrona
            try:
                representante_legal = self._extraer_representante_legal_sincrono(driver)
                print("✅ Representante legal extraído")
            except Exception as e:
                print(f"❌ Error en representante: {e}")
           
            distrito_obtenido = datos_basicos.get("distrito", "Sin datos")
            ubigeo = self.ubigeo_map.obtener_ubigeo(distrito_obtenido)

            # Crear el diccionario de respuesta
            resultado = {
                "numeroDocumento": ruc_numero,
                "razonSocial": datos_basicos.get("razon_social", "Sin datos"),
                "nombreComercial": datos_basicos.get("nombre_comercial", "-"),
                "activo": datos_basicos.get("estado_contribuyente", False),
                "condicion_contribuyente": datos_basicos.get("condicion_contribuyente", "Sin datos"),
                "direccion": datos_basicos.get("direccion", "Sin datos"),
                "distrito": datos_basicos.get("distrito", "Sin datos"),
                "provincia": datos_basicos.get("provincia", "Sin datos"),
                "ubigeo":ubigeo,
                "departamento": datos_basicos.get("departamento", "Sin datos"),
                "fechaInicioActividades": datos_basicos.get("fecha_inicio_actividades", "Sin datos"),
                "EsAgenteRetencion": datos_basicos.get("es_agente_retencion", False),
                "actividadEconomica": datos_basicos.get("actividad_economica", "Sin datos"),
                "tipoContribuyente": datos_basicos.get("tipo_contribuyente", "Sin datos"),
                "numeroTrabajadores": cantidad_trabajadores,
                "prestadoresdeServicios": cantidad_prestadores,
                "representanteLegal": representante_legal
            }
            
            print(f"Información extraída exitosamente para RUC: {ruc_numero}")
            return resultado 
            
        except Exception as e:
            print(f"Error al consultar RUC {ruc_numero}: {e}")
            return self._crear_respuesta_error(ruc_numero, str(e))

    def close(self):
        """Cierra el WebDriver del singleton. Solo usar al finalizar la aplicación."""
        self.driver_manager.cleanup()

    def _extraer_datos_basicos(self, driver) -> Dict:
        """Extrae los datos básicos del RUC - OPTIMIZADO"""
        try:
            datos = {}
            
            # Extraer todos los datos básicos en una sola pasada usando find_elements
            try:
                # Extraer Razón Social
                elemento_h4 = driver.find_element(By.XPATH, "//h4[contains(text(), 'Número de RUC:')]/parent::div/following-sibling::div/h4")
                texto_completo_razon_social = elemento_h4.text
                datos["razon_social"] = texto_completo_razon_social.split(' - ')[1].strip()
            except:
                datos["razon_social"] = "Sin datos"

            try:
                # Extraer Nombre Comercial
                elemento_p_nombre_comercial = driver.find_element(By.XPATH, "//h4[contains(text(), 'Nombre Comercial:')]/parent::div/following-sibling::div/p")
                datos["nombre_comercial"] = elemento_p_nombre_comercial.text.strip()
            except:
                datos["nombre_comercial"] = "-"

            try:
                # Extraer Estado del contribuyente
                elemento_p_estado_contribuyente = driver.find_element(By.XPATH, "//h4[contains(text(), 'Estado del Contribuyente:')]/parent::div/following-sibling::div/p")
                datos["estado_contribuyente"] = elemento_p_estado_contribuyente.text.strip()
                if(datos["estado_contribuyente"] == "ACTIVO"):
                    datos["estado_contribuyente"] = True
                else:
                    datos["estado_contribuyente"] = False
            except:
                datos["estado_contribuyente"] = False

            try:
                # Extraer Condición del contribuyente
                elemento_p_condicion_contribuyente = driver.find_element(By.XPATH, "//h4[contains(text(), 'Condición del Contribuyente:')]/parent::div/following-sibling::div/p")
                datos["condicion_contribuyente"] = elemento_p_condicion_contribuyente.text.strip()
            except:
                datos["condicion_contribuyente"] = "Sin datos"

            try:
                # Extraer Fecha de Inicio de Actividades
                elemento_p_fecha_inicio = driver.find_element(By.XPATH, "//h4[contains(text(), 'Fecha de Inicio de Actividades:')]/parent::div/following-sibling::div/p")
                datos["fecha_inicio_actividades"] = elemento_p_fecha_inicio.text.strip()
            except:
                datos["fecha_inicio_actividades"] = "Sin datos"

            try:
                # Extraer Tipo Contribuyente
                elemento_p_tipo_contribuyente = driver.find_element(By.XPATH, "//h4[contains(text(), 'Tipo Contribuyente:')]/parent::div/following-sibling::div/p")
                datos["tipo_contribuyente"] = elemento_p_tipo_contribuyente.text.strip()
            except:
                datos["tipo_contribuyente"] = "Sin datos"


            # Extraer Domicilio Fiscal (rápido)
            datos.update(self._extraer_domicilio_fiscal_rapido(driver))

            # Extraer Actividad Económica (rápido)
            datos["actividad_economica"] = self._extraer_actividad_economica_rapido(driver)

            # Extraer información de Padrones (rápido)
            datos["es_agente_retencion"] = self._extraer_padrones_rapido(driver)

            return datos
        except Exception as e:
            print(f"Error al extraer datos básicos: {e}")
            return {
                "razon_social": "Sin datos",
                "nombre_comercial": "-",
                "estado_contribuyente": False,
                "fecha_inicio_actividades": "Sin datos",
                "tipo_contribuyente": "Sin datos",
                "direccion": "Sin datos",
                "departamento": "Sin datos",
                "provincia": "Sin datos",
                "distrito": "Sin datos",
                "actividad_economica": "Sin datos",
                "es_agente_retencion": False,
                "condicion_contribuyente": "Sin datos"

            }

    def _extraer_domicilio_fiscal_rapido(self, driver) -> Dict:
        """Extrae domicilio fiscal - VERSIÓN RÁPIDA"""
        try:
            elemento_p_domicilio_fiscal = driver.find_element(By.XPATH, "//h4[contains(text(), 'Domicilio Fiscal:')]/parent::div/following-sibling::div/p")
            texto_completo_domicilio_fiscal = elemento_p_domicilio_fiscal.text

            if texto_completo_domicilio_fiscal == "-":
                return {
                    "direccion": "No especificado",
                    "departamento": "No especificado", 
                    "provincia": "No especificado",
                    "distrito": "No especificado"
                }

            partes = texto_completo_domicilio_fiscal.rsplit("-", 2)
            if len(partes) == 3:
                distrito = partes[2].strip()
                provincia = partes[1].strip()
                direccion_y_depto = partes[0].strip()

                partes_direccion = direccion_y_depto.rsplit(" ", 1)
                if len(partes_direccion) == 2:
                    departamento = partes_direccion[1].strip()
                    direccion = partes_direccion[0].strip()
                else:
                    direccion = direccion_y_depto
                    departamento = "No especificado"
            else:
                direccion = texto_completo_domicilio_fiscal.strip()
                departamento = provincia = distrito = "No especificado"



            return {
                "direccion": direccion,
                "departamento": departamento,
                "provincia": provincia,
                "distrito": distrito
            }
        except:
            return {
                "direccion": "Sin datos",
                "departamento": "Sin datos",
                "provincia": "Sin datos", 
                "distrito": "Sin datos"
            }

    def _extraer_actividad_economica_rapido(self, driver) -> str:
        """Extrae actividad económica - VERSIÓN RÁPIDA"""
        try:
            elemento_td_rubro = driver.find_element(By.XPATH, "//h4[contains(text(), 'Actividad(es) Económica(s):')]/parent::div/following-sibling::div/table/tbody/tr/td")
            texto_completo_rubro = elemento_td_rubro.text
            
            partes_rubro = texto_completo_rubro.rsplit(" - ")
            return partes_rubro[-1].strip() if len(partes_rubro) > 1 else "Sin datos"
        except:
            return "Sin datos"

    def _extraer_padrones_rapido(self, driver) -> bool:
        """Extrae padrones - VERSIÓN RÁPIDA"""
        try:
            elemento_td_padrones = driver.find_element(By.XPATH, "//h4[contains(text(), 'Padrones:')]/parent::div/following-sibling::div/table/tbody/tr/td")
            return elemento_td_padrones.text != "NINGUNO"
        except:
            return False
        
    def _extraer_cantidad_trabajadores_rapido(self, driver) -> tuple:
        """Extrae la cantidad de trabajadores y prestadores de servicio - VERSIÓN ULTRA RÁPIDA CON PARALELISMO"""
        try:
            # Usar lock para evitar conflictos en navegación paralela
            with threading.Lock():
                # Timeout más estable
                btn_consultar = WebDriverWait(driver, 8).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "btnInfNumTra"))
                )
                btn_consultar.click()

                # Esperar tabla con timeout razonable
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "formEnviar"))
                )

                cantidad_trabajadores = "Sin datos"
                cantidad_prestadores_servicio = "Sin datos"
                
                try:
                    # Buscar filas con manejo de elementos obsoletos
                    filas = driver.find_elements(By.XPATH, "//table[@class='table']//tbody/tr")
                    
                    if len(filas) > 0:
                        try:
                            # Obtener la última fila con manejo de elementos obsoletos
                            ultima_fila = filas[-1]
                            celdas = ultima_fila.find_elements(By.TAG_NAME, "td")
                            
                            if len(celdas) >= 4:
                                cantidad_trabajadores = celdas[1].text.strip()
                                cantidad_prestadores_servicio = celdas[3].text.strip()
                        except:
                            pass  # Ignorar errores de lectura
                except Exception as e:
                    print(f"Error al procesar filas de trabajadores: {e}")

                # Volver inmediatamente sin esperas
                try:
                    btn_volver = driver.find_element(By.CLASS_NAME, "btnNuevaConsulta")
                    btn_volver.click()
                except:
                    pass  # Ignorar errores de navegación

                return cantidad_trabajadores, cantidad_prestadores_servicio
            
        except Exception as e:
            print(f"Error en _extraer_cantidad_trabajadores_rapido: {e}")
            return "Sin datos", "Sin datos"

   
    def _extraer_representante_legal_sincrono(self, driver) -> Dict:
        """Extrae información del representante legal - VERSIÓN SÍNCRONA"""
        try:
            # Hacer clic en representantes legales con timeout estable
            btn_representates_legales = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "btnInfRepLeg"))
            )
            btn_representates_legales.click()

            # Esperar tabla con timeout razonable
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//table[@class='table']//tbody/tr"))
            )

            # Valores por defecto
            documento_representante = "Sin datos"
            nro_documento_representante = "Sin datos"
            nombre_representante = "Sin datos"
            cargo_representante = "Sin datos"
            fecha_representante = "Sin datos"
            
            try:
                # Obtener filas inmediatamente
                filas = driver.find_elements(By.XPATH, "//table[@class='table']//tbody/tr")
                
                # Buscar gerente o usar primera fila rápidamente
                fila_seleccionada = None
                for fila in filas[:3]:  # Solo revisar las primeras 3 filas
                    celdas = fila.find_elements(By.TAG_NAME, "td")
                    if len(celdas) >= 4 and "GERENTE" in celdas[3].text.upper():
                        fila_seleccionada = fila
                        break
                
                # Si no encuentra gerente, usar primera fila
                if not fila_seleccionada and len(filas) > 0:
                    fila_seleccionada = filas[0]
                
                if fila_seleccionada:
                    celdas = fila_seleccionada.find_elements(By.TAG_NAME, "td")
                    if len(celdas) >= 5:
                        documento_representante = celdas[0].text.strip()
                        nro_documento_representante = celdas[1].text.strip()
                        nombre_representante = celdas[2].text.strip()
                        cargo_representante = celdas[3].text.strip()
                        fecha_representante = celdas[4].text.strip()
                    
            except Exception as e:
                print(f"Error leyendo representante: {e}")

            return {
                "tipoDocumento": documento_representante,
                "nroDocumento": nro_documento_representante,
                "nombre": nombre_representante,
                "cargo": cargo_representante,
                "fechaDesde": fecha_representante
            }
            
        except Exception as e:
            print(f"Error rápido en representante: {e}")
            return {
                "tipoDocumento": "Sin datos",
                "nroDocumento": "Sin datos",
                "nombre": "Sin datos",
                "cargo": "Sin datos",
                "fechaDesde": "Sin datos"
            }

  
    def _crear_respuesta_error(self, ruc_numero: str, error_msg: str) -> Dict:
        """Crea una respuesta de error estandarizada"""
        return {
            "numeroDocumento": ruc_numero,
            "razonSocial": "Error en consulta",
            "nombreComercial": "Sin datos",
            "activo": False,
            "direccion": "Sin datos",
            "distrito": "Sin datos",
            "provincia": "Sin datos",
            "departamento": "Sin datos",
            "fechaInicioActividades": "Sin datos",
            "EsAgenteRetencion": False,
            "actividadEconomica": "Sin datos",
            "tipoContribuyente": "Sin datos",
            "numeroTrabajadores": "Sin datos",
            "prestadoresdeServicios": "Sin datos",
            "representanteLegal": {
                "tipoDocumento": "Sin datos",
                "nroDocumento": "Sin datos",
                "nombre": "Sin datos",
                "cargo": "Sin datos",
                "fechaDesde": "Sin datos"
            },
            "error": error_msg
        }




