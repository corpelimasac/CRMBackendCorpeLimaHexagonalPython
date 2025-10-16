import pandas as pd
import pickle
import os
import threading
from typing import Dict, Optional, Any # Nuevo import para tipos
from app.adapters.outbound.external_services.sunat.dto import DatosRucDTO, RepresentanteLegalDTO
from playwright.sync_api import sync_playwright, Page

# Obtener el directorio donde está ubicado este archivo
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NOMBRE_CSV = os.path.join(SCRIPT_DIR, 'ubigeo_distritos.csv')
NOMBRE_PICKLE = os.path.join(SCRIPT_DIR, 'ubigeo_map.pkl')


def get_archivo_pickle():
    # Implementación mínima para satisfacer tu esqueleto original
    return NOMBRE_PICKLE


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


def _extraer_trabajadores(page: Page, dto: DatosRucDTO) -> None:
  """Extrae información de trabajadores y prestadores de servicios"""
  try:
    boton_trabajadores_loc = page.locator('.btnInfNumTra')

    if boton_trabajadores_loc.is_visible():
        boton_trabajadores_loc.click()
        page.wait_for_load_state('networkidle')

        if page.locator('table.table').is_visible():
            ultima_fila = page.locator('table.table tbody tr').last
            dto.numero_trabajadores = ultima_fila.locator('td').nth(1).text_content()
            dto.prestadores_de_servicios = ultima_fila.locator('td').nth(3).text_content()
            page.click('.btnNuevaConsulta')
            page.wait_for_load_state('networkidle')
  except Exception as e:
    print(f"Error al extraer trabajadores: {e}")


def _extraer_rubros(page: Page, dto: DatosRucDTO) -> None:
  """Extrae actividades económicas y las asigna al DTO"""
  try:
    tabla_rubros = page.locator('.tblResultado').nth(0)
    filas_en_tabla = tabla_rubros.locator('tr')
    numero_filas = filas_en_tabla.count()

    if numero_filas >= 1:
        dto.actividad_economica = filas_en_tabla.nth(0).text_content().strip()

    if numero_filas >= 2:
        dto.actividad_economica2 = filas_en_tabla.nth(1).text_content().strip()
    else:
        print("Solo se encontró una actividad económica.")
  except Exception as e:
    print(f"Error al extraer rubros: {e}")


class SunatScrapper:
  """
  Servicio que realiza web scraping en la pagina de la SUNAT
  """

  def __init__(self, headless: bool = True) -> None:
    self.url = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/FrameCriterioBusquedaWeb.jsp"
    self.ubigeo_map = UbigeoMap()
    self.headless = headless  # Por defecto True para Docker/producción

  def consultar_ruc(self,ruc_numero)->Dict:
    """
        Realiza web scraping en la página de la SUNAT para obtener datos de un RUC.

        Args:
            ruc_numero (str): Número de RUC a consultar
        Returns:
            dict: Diccionario con toda la información del RUC
    """

    try:
      with sync_playwright() as p:
        # Lanzar navegador con argumentos para evitar detección
        browser = p.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )

        # Crear contexto con user agent realista
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='es-PE',
            timezone_id='America/Lima'
        )

        page = context.new_page()

        # Navegar con timeout más largo y esperar hasta networkidle
        page.goto(self.url, wait_until='networkidle', timeout=60000)

        # Esperar un poco para simular comportamiento humano
        page.wait_for_timeout(1000)

        page.fill('#txtRuc', ruc_numero)
        page.wait_for_timeout(500)

        page.click('#btnAceptar')
        page.wait_for_load_state('networkidle', timeout=60000)
        page.wait_for_selector('h4.list-group-item-heading', timeout=30000)

        print("Extrayendo información...")

        # Inicializar DTO
        dto = DatosRucDTO(numero_documento=ruc_numero)

        # Extraer datos y poblar DTO
        self._extraer_datos_basicos(page, dto)
        _extraer_trabajadores(page, dto)
        page.wait_for_timeout(1000)
        self._extraer_representantes_legales(page, dto)

        context.close()
        browser.close()

      return dto.to_dict()

    except Exception as e:
      print(f"Error al consultar RUC {ruc_numero}: {e}")
      return DatosRucDTO.crear_error(ruc_numero, str(e)).to_dict()

  def _extraer_datos_basicos(self, page: Page, dto: DatosRucDTO) -> None:
    """Extrae datos básicos y los asigna al DTO"""
    try:
      ruc_info = page.locator('h4.list-group-item-heading').nth(1).inner_text()
      dto.razon_social = ruc_info.split(' - ')[1].strip()

      dto.tipo_contribuyente = page.locator('p.list-group-item-text').nth(0).inner_text()
      dto.nombre_comercial = page.locator('p.list-group-item-text').nth(1).inner_text()
      dto.fecha_inicio_actividades = page.locator('p.list-group-item-text').nth(3).inner_text()
      dto.activo = page.locator('p.list-group-item-text').nth(4).inner_text() == "ACTIVO"
      dto.condicion_contribuyente = page.locator('p.list-group-item-text').nth(5).inner_text()

      texto_completo_domicilio_fiscal = page.locator('p.list-group-item-text').nth(6).inner_text()

      if texto_completo_domicilio_fiscal == "-":
          dto.direccion = "No especificado"
          dto.departamento = "No especificado"
          dto.provincia = "No especificado"
          dto.distrito = "No especificado"
      else:
          partes = texto_completo_domicilio_fiscal.rsplit("-", 2)
          if len(partes) == 3:
              dto.distrito = partes[2].strip()
              dto.provincia = partes[1].strip()
              direccion_y_depto = partes[0].strip()

              partes_direccion = direccion_y_depto.rsplit(" ", 1)
              if len(partes_direccion) == 2:
                  dto.departamento = partes_direccion[1].strip()
                  dto.direccion = partes_direccion[0].strip()
              else:
                  dto.direccion = direccion_y_depto
                  dto.departamento = "No especificado"
          else:
              dto.direccion = texto_completo_domicilio_fiscal.strip()
              dto.departamento = dto.provincia = dto.distrito = "No especificado"

      dto.ubigeo = self.ubigeo_map.obtener_ubigeo(dto.distrito)

      # Extraer rubros
      _extraer_rubros(page, dto)

      # Verificar agente de retención
      tabla_agente = page.locator('.tblResultado').nth(3)
      primera_fila = tabla_agente.locator('tr').nth(0).text_content()
      dto.es_agente_retencion = primera_fila != "NINGUNO"

    except Exception as e:
      print(f"Error al extraer datos básicos: {e}")
      dto.error = str(e)

  @staticmethod
  def _extraer_representantes_legales(page: Page, dto: DatosRucDTO) -> None:
    """Extrae información del representante legal"""
    try:
      boton_representantes_loc = page.locator('.btnInfRepLeg')
      print("Buscando botón de Representantes Legales...")

      boton_representantes_loc.click(timeout=5000) 

        # Si el click tuvo éxito, esperamos a que la nueva información cargue.
      page.wait_for_load_state('networkidle', timeout=10000)
      tabla_representantes_loc = page.locator('table.table')
      tabla_representantes_loc.wait_for(state='visible', timeout=5000)
      primera_fila = tabla_representantes_loc.locator('tbody tr').first
        
      dto.representante_legal = RepresentanteLegalDTO(
            tipo_documento=primera_fila.locator('td').nth(0).text_content().strip(),
            nro_documento=primera_fila.locator('td').nth(1).text_content().strip(),
            nombre=primera_fila.locator('td').nth(2).text_content().strip(),
            cargo=primera_fila.locator('td').nth(3).text_content().strip(),
            fecha_desde=primera_fila.locator('td').nth(4).text_content().strip()
        )
      print("Representante legal extraído con éxito.")

    except TimeoutError:
        # Esto es normal si el RUC no tiene representantes legales visibles.
        # El error ocurre porque el .click() esperó 5 segundos y el botón nunca apareció.
        print("No se encontró el botón de Representantes Legales. Se asume que no existe para este RUC.")
    except Exception as e:
        # Captura cualquier otro error inesperado durante la extracción.
        print(f"Error inesperado al extraer representantes legales: {e}")

    