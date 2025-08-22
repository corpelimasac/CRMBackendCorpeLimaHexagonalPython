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


class SunatScraper:
    """
    Servicio para realizar web scraping en la página de SUNAT
    """
    
    def __init__(self):
        self.url = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/FrameCriterioBusquedaWeb.jsp"
    
    def consultar_ruc_basico(self, ruc_numero: str) -> Dict:
        """
        Consulta ultra-rápida que solo obtiene datos básicos esenciales.
        
        Args:
            ruc_numero (str): Número de RUC a consultar
            
        Returns:
            dict: Diccionario con información básica del RUC
        """
        driver = None
        try:
            # Configuración mínima para máxima velocidad
            options = ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-images")
            options.add_argument("--disable-javascript")
            options.add_argument("--window-size=800,600")
            options.add_argument("--page-load-strategy=eager")

            # ChromeDriver
            try:
                import os
                import glob
                
                chromedriver_paths = [
                    '/usr/bin/chromedriver',
                    '/usr/local/bin/chromedriver',
                    '/opt/chromedriver/chromedriver'
                ]
                
                selenium_paths = glob.glob('/opt/selenium/chromedriver-*/chromedriver')
                chromedriver_paths.extend(selenium_paths) 
                
                chromedriver_path = None
                for path in chromedriver_paths:
                    if os.path.exists(path) and os.access(path, os.X_OK):
                        chromedriver_path = path
                        break
                
                if chromedriver_path:
                    service = ChromeService(executable_path=chromedriver_path)
                else:
                    service = ChromeService(executable_path=ChromeDriverManager().install())
            except Exception:
                service = ChromeService(executable_path=ChromeDriverManager().install())

            driver = webdriver.Chrome(service=service, options=options)
            
            # Timeouts ultra-cortos
            driver.set_page_load_timeout(8)
            driver.implicitly_wait(0.5)

            # Navegación y consulta
            driver.get(self.url)
            
            ruc_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "txtRuc"))
            )
            ruc_input.clear()
            ruc_input.send_keys(ruc_numero)
            
            btn_consultar = driver.find_element(By.ID, "btnAceptar")
            btn_consultar.click()

            WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.CLASS_NAME, "list-group"))
            )

            # Solo datos básicos esenciales
            datos_basicos = self._extraer_datos_basicos(driver)
            
            return {
                "numeroDocumento": ruc_numero,
                "razonSocial": datos_basicos.get("razon_social", "Sin datos"),
                "nombreComercial": datos_basicos.get("nombre_comercial", "-"),
                "direccion": datos_basicos.get("direccion", "Sin datos"),
                "distrito": datos_basicos.get("distrito", "Sin datos"),
                "provincia": datos_basicos.get("provincia", "Sin datos"),
                "departamento": datos_basicos.get("departamento", "Sin datos"),
                "fechaInicioActividades": datos_basicos.get("fecha_inicio_actividades", "Sin datos"),
                "EsAgenteRetencion": datos_basicos.get("es_agente_retencion", False),
                "actividadEconomica": datos_basicos.get("actividad_economica", "Sin datos"),
                "tipoContribuyente": datos_basicos.get("tipo_contribuyente", "Sin datos"),
                "numeroTrabajadores": "Sin datos",  # Omitido por velocidad
                "prestadoresdeServicios": "Sin datos",  # Omitido por velocidad
                "representanteLegal": {
                    "tipoDocumento": "Sin datos",
                    "nroDocumento": "Sin datos",
                    "nombre": "Sin datos",
                    "cargo": "Sin datos",
                    "fechaDesde": "Sin datos"
                }
            }
            
        except Exception as e:
            return self._crear_respuesta_error(ruc_numero, str(e))
        finally:
            if driver:
                driver.quit()

    def consultar_ruc(self, ruc_numero: str, modo_rapido: bool = True) -> Dict:
        """
        Realiza web scraping en la página de la SUNAT para obtener datos de un RUC.
        
        Args:
            ruc_numero (str): Número de RUC a consultar
            modo_rapido (bool): Si True, omite secciones lentas para máxima velocidad
            
        Returns:
            dict: Diccionario con toda la información del RUC
        """
        driver = None
        try:
            # Configurar opciones de Chrome optimizadas para velocidad máxima
            options = ChromeOptions()
            
            # User-Agent ligero
            user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            options.add_argument(f'user-agent={user_agent}')
            
            # Opciones críticas para máxima velocidad
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-software-rasterizer")
            
            # Deshabilitar todo lo innecesario para velocidad
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")
            options.add_argument("--disable-javascript")  # SUNAT funciona sin JS para consultas básicas
            options.add_argument("--disable-css")
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-features=VizDisplayCompositor,TranslateUI")
            options.add_argument("--disable-background-networking")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-renderer-backgrounding")
            options.add_argument("--disable-backgrounding-occluded-windows")
            options.add_argument("--disable-client-side-phishing-detection")
            options.add_argument("--disable-sync")
            options.add_argument("--disable-default-apps")
            options.add_argument("--no-first-run")
            options.add_argument("--no-default-browser-check")
            options.add_argument("--disable-logging")
            options.add_argument("--disable-gpu-logging")
            
            # Optimizaciones de memoria y red
            options.add_argument("--memory-pressure-off")
            options.add_argument("--aggressive-cache-discard")
            options.add_argument("--window-size=800,600")  # Ventana más pequeña
            
            # Estrategia de carga más agresiva
            options.add_argument("--page-load-strategy=eager")
            
            # Configurar prefs para máxima velocidad
            prefs = {
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_setting_values.notifications": 2,
                "profile.managed_default_content_settings.media_stream": 2,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.geolocation": 2,
                "profile.default_content_setting_values.plugins": 2,
                "profile.managed_default_content_settings.stylesheets": 2,
                "profile.managed_default_content_settings.javascript": 1,  # Permitir JS mínimo
            }
            options.add_experimental_option("prefs", prefs)
            
            # Anti-detección mínima
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            # Intentar usar ChromeDriver del sistema primero, luego WebDriverManager
            try:
                import os
                import glob
                
                # Rutas posibles para ChromeDriver
                chromedriver_paths = [
                    '/usr/bin/chromedriver',
                    '/usr/local/bin/chromedriver',
                    '/opt/chromedriver/chromedriver'
                ]
                
                # Buscar en directorios de Selenium también
                selenium_paths = glob.glob('/opt/selenium/chromedriver-*/chromedriver')
                chromedriver_paths.extend(selenium_paths)
                
                chromedriver_path = None
                for path in chromedriver_paths:
                    if os.path.exists(path) and os.access(path, os.X_OK):
                        chromedriver_path = path
                        break
                
                if chromedriver_path:
                    service = ChromeService(executable_path=chromedriver_path)
                    print(f"Usando ChromeDriver del sistema: {chromedriver_path}")
                else:
                    print("ChromeDriver no encontrado en el sistema, usando WebDriverManager")
                    service = ChromeService(executable_path=ChromeDriverManager().install())
                    print("Usando ChromeDriver de WebDriverManager")
            except Exception as e:
                print(f"Error configurando ChromeDriver: {e}")
                print("Fallback a WebDriverManager")
                service = ChromeService(executable_path=ChromeDriverManager().install())

            driver = webdriver.Chrome(service=service, options=options)
            
            # Configurar timeouts agresivos para velocidad
            driver.set_page_load_timeout(10)  # Timeout reducido
            driver.set_script_timeout(5)      # Timeout muy corto para scripts
            driver.implicitly_wait(1)         # Timeout implícito mínimo

            print(f"Consultando RUC {ruc_numero} en SUNAT...")
            driver.get(self.url)

            # Esperar y llenar el campo de RUC más rápido
            ruc_input = WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.ID, "txtRuc"))
            )
            ruc_input.clear()
            ruc_input.send_keys(ruc_numero)

            # Hacer clic en el botón de buscar inmediatamente
            btn_consultar = driver.find_element(By.ID, "btnAceptar")
            btn_consultar.click()

            print("Extrayendo información...")

            # Esperar resultados con timeout reducido
            WebDriverWait(driver, 12).until(
                EC.presence_of_element_located((By.CLASS_NAME, "list-group"))
            )

            # Extraer información básica (siempre necesaria)
            datos_basicos = self._extraer_datos_basicos(driver)
            
            # Extraer información adicional de forma paralela y rápida
            cantidad_trabajadores = "Sin datos"
            cantidad_prestadores = "Sin datos"
            representante_legal = {
                "tipoDocumento": "Sin datos",
                "nroDocumento": "Sin datos", 
                "nombre": "Sin datos",
                "cargo": "Sin datos",
                "fechaDesde": "Sin datos"
            }
            
            # Extraer información adicional según el modo
            if modo_rapido:
                # Modo rápido: intentar con timeouts muy cortos
                try:
                    print("Extrayendo cantidad de trabajadores (modo rápido)...")
                    cantidad_trabajadores, cantidad_prestadores = self._extraer_cantidad_trabajadores_rapido(driver)
                except Exception as e:
                    print(f"Omitiendo trabajadores por velocidad: {e}")
                
                try:
                    print("Extrayendo representante legal (modo rápido)...")
                    representante_legal = self._extraer_representante_legal_rapido(driver)
                except Exception as e:
                    print(f"Omitiendo representante legal por velocidad: {e}")
            else:
                # Modo completo: usar métodos originales
                try:
                    print("Extrayendo cantidad de trabajadores (modo completo)...")
                    cantidad_trabajadores, cantidad_prestadores = self._extraer_cantidad_trabajadores(driver)
                except Exception as e:
                    print(f"Error al extraer trabajadores: {e}")
                
                try:
                    print("Extrayendo representante legal (modo completo)...")
                    representante_legal = self._extraer_representante_legal(driver)
                except Exception as e:
                    print(f"Error al extraer representante legal: {e}")

            # Crear el diccionario de respuesta
            resultado = {
                "numeroDocumento": ruc_numero,
                "razonSocial": datos_basicos.get("razon_social", "Sin datos"),
                "nombreComercial": datos_basicos.get("nombre_comercial", "-"),
                "direccion": datos_basicos.get("direccion", "Sin datos"),
                "distrito": datos_basicos.get("distrito", "Sin datos"),
                "provincia": datos_basicos.get("provincia", "Sin datos"),
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
        finally:
            if driver:
                driver.quit()

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
                "fecha_inicio_actividades": "Sin datos",
                "tipo_contribuyente": "Sin datos",
                "direccion": "Sin datos",
                "departamento": "Sin datos",
                "provincia": "Sin datos",
                "distrito": "Sin datos",
                "actividad_economica": "Sin datos",
                "es_agente_retencion": False
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

    def _extraer_domicilio_fiscal(self, driver) -> Dict:
        """Extrae y procesa la información del domicilio fiscal"""
        try:
            xpath_domicilio_fiscal = "//h4[contains(text(), 'Domicilio Fiscal:')]/parent::div/following-sibling::div/p"
            elemento_p_domicilio_fiscal = driver.find_element(By.XPATH, xpath_domicilio_fiscal)
            texto_completo_domicilio_fiscal = elemento_p_domicilio_fiscal.text

            direccion = "No especificado"
            departamento = "No especificado"
            provincia = "No especificado"
            distrito = "No especificado"

            if texto_completo_domicilio_fiscal != "-":
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
                else:
                    direccion = texto_completo_domicilio_fiscal.strip()

            return {
                "direccion": direccion,
                "departamento": departamento,
                "provincia": provincia,
                "distrito": distrito
            }
        except Exception as e:
            print(f"Error al extraer domicilio fiscal: {e}")
            return {
                "direccion": "Sin datos",
                "departamento": "Sin datos",
                "provincia": "Sin datos",
                "distrito": "Sin datos"
            }

    def _extraer_actividad_economica(self, driver) -> str:
        """Extrae la actividad económica"""
        try:
            xpath_rubro = "//h4[contains(text(), 'Actividad(es) Económica(s):')]/parent::div/following-sibling::div/table/tbody/tr/td"
            elemento_td_rubro = driver.find_element(By.XPATH, xpath_rubro)
            texto_completo_rubro = elemento_td_rubro.text
            
            partes_rubro = texto_completo_rubro.rsplit(" - ")
            if len(partes_rubro) > 1:
                return partes_rubro[-1].strip()
            else:
                return "Sin datos"
        except Exception as e:
            print(f"Error al extraer actividad económica: {e}")
            return "Sin datos"

    def _extraer_padrones(self, driver) -> bool:
        """Extrae información de padrones"""
        try:
            xpath_padrones = "//h4[contains(text(), 'Padrones:')]/parent::div/following-sibling::div/table/tbody/tr/td"
            elemento_td_padrones = driver.find_element(By.XPATH, xpath_padrones)
            texto_completo_padrones = elemento_td_padrones.text
            return texto_completo_padrones != "NINGUNO"
        except Exception as e:
            print(f"Error al extraer padrones: {e}")
            return False

    def _extraer_cantidad_trabajadores_rapido(self, driver) -> tuple:
        """Extrae la cantidad de trabajadores y prestadores de servicio - VERSIÓN RÁPIDA"""
        try:
            # Hacer clic en el botón con timeout muy corto
            btn_consultar = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "btnInfNumTra"))
            )
            btn_consultar.click()

            # Esperar tabla con timeout reducido
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.NAME, "formEnviar"))
            )

            cantidad_trabajadores = "Sin datos"
            cantidad_prestadores_servicio = "Sin datos"
            
            # Buscar filas inmediatamente sin espera extra
            filas = driver.find_elements(By.XPATH, "//table[@class='table']//tbody/tr")
            
            if len(filas) > 0:
                try:
                    ultima_fila = filas[-1]
                    celdas = ultima_fila.find_elements(By.TAG_NAME, "td")
                    
                    if len(celdas) >= 4:
                        cantidad_trabajadores = celdas[1].text.strip()
                        cantidad_prestadores_servicio = celdas[3].text.strip()
                except Exception as e:
                    print(f"Error leyendo tabla: {e}")

            # Volver rápidamente sin esperas
            try:
                btn_volver = driver.find_element(By.CLASS_NAME, "btnNuevaConsulta")
                btn_volver.click()
                # Sin sleep - continuar inmediatamente
            except:
                pass  # Ignorar errores de navegación

            return cantidad_trabajadores, cantidad_prestadores_servicio
            
        except Exception as e:
            print(f"Error rápido en trabajadores: {e}")
            return "Sin datos", "Sin datos"

    def _extraer_cantidad_trabajadores(self, driver) -> tuple:
        """Extrae la cantidad de trabajadores y prestadores de servicio"""
        try:
            # Hacer clic en el botón de Cantidad de Trabajadores
            
            btn_consultar = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "btnInfNumTra"))
            )
            btn_consultar.click()

            # Esperar a que la tabla aparezca
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.NAME, "formEnviar"))
            )

            cantidad_trabajadores = "Sin datos"
            cantidad_prestadores_servicio = "Sin datos"
            
            # Verificar si existe al menos una fila en la tabla
            xpath_verificar_filas = "//table[@class='table']//tbody/tr"
            filas = driver.find_elements(By.XPATH, xpath_verificar_filas)
            
            if len(filas) > 0:
                # Obtener la última fila directamente
                try:
                    ultima_fila = filas[-1]  # Obtener la última fila directamente
                    celdas = ultima_fila.find_elements(By.TAG_NAME, "td")
                    
                    if len(celdas) >= 4:
                        cantidad_trabajadores = celdas[1].text.strip()
                        cantidad_prestadores_servicio = celdas[3].text.strip()
                except Exception as e:
                    print(f"Error al leer celdas de la tabla: {e}")

            # Volver a la página principal más rápido
            try:
                btn_volver = WebDriverWait(driver, 8).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "btnNuevaConsulta"))
                )
                btn_volver.click()
                time.sleep(1)  # Reducir tiempo de espera
            except Exception as e:
                print(f"Error al volver a la página principal: {e}")

            return cantidad_trabajadores, cantidad_prestadores_servicio
            
        except Exception as e:
            print(f"Error al extraer cantidad de trabajadores: {e}")
            return "Sin datos", "Sin datos"

    def _extraer_representante_legal_rapido(self, driver) -> Dict:
        """Extrae información del representante legal - VERSIÓN RÁPIDA"""
        try:
            # Hacer clic en representantes legales con timeout corto
            btn_representates_legales = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "btnInfRepLeg"))
            )
            btn_representates_legales.click()

            # Esperar tabla con timeout muy corto
            WebDriverWait(driver, 4).until(
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

    def _extraer_representante_legal(self, driver) -> Dict:
        """Extrae información del representante legal"""
        try:
            # Hacer clic en el botón de representantes legales
            btn_representates_legales = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "btnInfRepLeg"))
            )
            btn_representates_legales.click()
            time.sleep(1)  # Reducir tiempo de espera

            # Esperar a que la tabla aparezca
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//table[@class='table']//tbody/tr"))
            )

            # Inicializar variables del representante legal
            documento_representante = "Sin datos"
            nro_documento_representante = "Sin datos"
            nombre_representante = "Sin datos"
            cargo_representante = "Sin datos"
            fecha_representante = "Sin datos"
            
            try:
                # Obtener todas las filas de una vez
                filas = driver.find_elements(By.XPATH, "//table[@class='table']//tbody/tr")
                
                # Buscar primero GERENTE GENERAL
                fila_gerente = None
                for fila in filas:
                    celdas = fila.find_elements(By.TAG_NAME, "td")
                    if len(celdas) >= 4 and "GERENTE" in celdas[3].text.upper():
                        fila_gerente = fila
                        break
                
                # Si no se encuentra gerente, usar la primera fila
                if not fila_gerente and len(filas) > 0:
                    fila_gerente = filas[0]
                
                if fila_gerente:
                    celdas = fila_gerente.find_elements(By.TAG_NAME, "td")
                    if len(celdas) >= 5:
                        documento_representante = celdas[0].text.strip()
                        nro_documento_representante = celdas[1].text.strip()
                        nombre_representante = celdas[2].text.strip()
                        cargo_representante = celdas[3].text.strip()
                        fecha_representante = celdas[4].text.strip()
                    
            except Exception as e:
                print(f"Error al extraer datos de representantes legales: {e}")

            return {
                "tipoDocumento": documento_representante,
                "nroDocumento": nro_documento_representante,
                "nombre": nombre_representante,
                "cargo": cargo_representante,
                "fechaDesde": fecha_representante
            }
            
        except Exception as e:
            print(f"Error al extraer representante legal: {e}")
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
