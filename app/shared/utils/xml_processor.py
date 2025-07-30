import xml.etree.ElementTree as ET  # Módulo para parsear XML como árbol de elementos
from datetime import datetime        # Para manejo y formateo de fechas
import locale                        # Para configurar la localización de fechas

# Configuración de la localización al español de España,
# necesario para que los nombres de los meses salgan en español
try:
    # Intenta configurar el locale español
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    try:
        # Fallback a español genérico
        locale.setlocale(locale.LC_TIME, 'es_ES')
    except locale.Error:
        # Usa el locale del sistema si todo falla
        locale.setlocale(locale.LC_TIME, '')
        # O simplemente omite la configuración
        print("⚠️ Advertencia: No se pudo configurar el locale español")
        
class InvoiceExtractor:
    """
    Clase encargada de:
      1. Parsear un archivo XML de factura (UBL)
      2. Extraer datos relevantes: número de factura, cotización, cliente, líneas, fecha.
      3. Proveer esos datos formateados para generarlos en un PDF u otro uso.

    Atributos:
    - tree: Árbol de nodos XML parseado
    - root: Nodo raíz del árbol
    - namespaces: Diccionario de prefijos y URIs XML
    - num_coti: Texto de la nota que contiene "COTIZACION"
    """
    def __init__(self, xml_file):
        # 1. Parseamos el XML y guardamos el árbol y el nodo raíz
        self.tree = ET.parse(xml_file)
        self.root = self.tree.getroot()

        # 2. Definimos los namespaces(nombre de espacios) UBL para búsquedas con prefijos
        ## Cada nombre de espacio se identifica con una URI(Uniform Resource Identifier)
        ## El prefijo se usa para identificar el espacio en el XML
        ## El valor es la URI del espacio
        self.namespaces = {
            '': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',  
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2'
        }
        # 3. Inicializamos los atributos que vamos a extraer
        self.num_coti = None
        self.registration_name = None
        self.fact=None
        self.date=None
        self.detalles = []

    def extract_num_coti(self):
        # 1. Buscamos todas las etiquetas cbc:Note en el XML
        notes = self.root.findall('.//cbc:Note', self.namespaces)
        for note in notes:
            if "COTIZACION" in note.text:
                # 2. Si encontramos una nota que contiene "COTIZACION", la guardamos
                self.num_coti = note.text
                break
        else:
            print('In XMLProcessor: No se encontró la COTIZACION.')

    def extract_num_fact(self):
        # 1. Buscamos la etiqueta cbc:ID en el XML
        fact= self.root.find('.//cbc:ID', self.namespaces)
        if fact is not None:
            # 2. Si encontramos la etiqueta, guardamos el texto
            self.fact = fact.text
        else:
            print('In XMLProcessor: No se encontró la etiqueta cbc:ID')

    def extract_fecha(self):
        """Extrae la fecha de <cbc:IssueDate>, la convierte a datetime,
        y la formatea como "DD de <Mes> del YYYY".
        """
        # 1. Buscamos la etiqueta cbc:IssueDate en el XML
        date = self.root.find('.//cbc:IssueDate', self.namespaces)
        if date is not None:
            # Ajusta el formato de acuerdo con el formato de fecha en tu XML
            fecha_objeto_xml = datetime.strptime(date.text, "%Y-%m-%d")  # Especifica el formato
            dia_xml = fecha_objeto_xml.strftime("%d")  # Extrae el día
            mes_xml = fecha_objeto_xml.strftime("%B")  # Extrae el mes en formato textual (español)
            anio_xml = fecha_objeto_xml.strftime("%Y")  # Extrae el año
            
            # Formatea la fecha como 'día de mes del año'
            self.date = f"{dia_xml} de {mes_xml} del {anio_xml}"
        else:
            print('No se encontró la etiqueta cbc:IssueDate')

    def extract_registration_name(self):
        """
        Extrae el nombre o razón social del cliente.
        Navega por:
          <cac:AccountingCustomerParty>
            └─ <cac:PartyLegalEntity>
                 └─ <cbc:RegistrationName>
        para obtener el nombre o razón social del cliente.
        """
        # 1. Buscamos la etiqueta cac:AccountingCustomerParty en el XML
        accounting_customer_party = self.root.find('.//cac:AccountingCustomerParty', self.namespaces)
        if accounting_customer_party is not None:
            # 2. Buscamos la etiqueta cac:PartyLegalEntity dentro de cac:AccountingCustomerParty
            party_legal_entity = accounting_customer_party.find('.//cac:PartyLegalEntity', self.namespaces)
            if party_legal_entity is not None:
                # 3. Buscamos la etiqueta cbc:RegistrationName dentro de cac:PartyLegalEntity
                registration_name_element = party_legal_entity.find('cbc:RegistrationName', self.namespaces)
                self.registration_name = registration_name_element.text if registration_name_element is not None else 'No disponible'
            else:
                print('No se encontró la etiqueta cac:PartyLegalEntity')
        else:
            print('No se encontró la etiqueta cac:AccountingCustomerParty')

    def extract_invoice_lines(self):
        """
        Extrae las líneas de detalle de la factura.
        Navega por:
          <cac:InvoiceLine>
            └─ <cbc:InvoicedQuantity>
                 └─ <cbc:Note>
                      └─ <cac:Item>
                           └─ <cbc:Description>
        para obtener la cantidad, unidad y descripción de cada línea.
        """
        # 1. Buscamos todas las etiquetas cac:InvoiceLine en el XML
        invoice_lines = self.root.findall('.//cac:InvoiceLine', self.namespaces)
        for line in invoice_lines:
            # 2. Para cada línea, extraemos la cantidad, unidad y descripción
            cant = self._get_element_text(line, 'cbc:InvoicedQuantity')
            und = self._get_element_text(line, 'cbc:Note')
            description_value = self._get_item_description(line)
            self.detalles.append((cant, und, description_value))

    def _get_element_text(self, element, tag):
        """Método auxiliar para obtener el texto de un elemento XML seguro."""
        tag_element = element.find(tag, self.namespaces)
        return tag_element.text if tag_element is not None else 'No disponible'

    def _get_item_description(self, line):
        """Método auxiliar para obtener la descripción de un elemento."""
        item = line.find('cac:Item', self.namespaces)
        if item is not None:
            description_element = item.find('cbc:Description', self.namespaces)
            return description_element.text if description_element is not None else 'No disponible'
        return 'No disponible'

    def extract_data(self):
        """Ejecuta todas las extracciones."""
        self.extract_num_fact()
        self.extract_num_coti()
        self.extract_registration_name()
        self.extract_invoice_lines()
        self.extract_fecha()

    def get_data(self):
        # 1. Devolvemos los datos extraídos en el orden correcto
        return self.registration_name, self.num_coti, self.fact, self.detalles, self.date, f"CARTA DE GARANTIA - {self.registration_name}_{self.date}.pdf" 