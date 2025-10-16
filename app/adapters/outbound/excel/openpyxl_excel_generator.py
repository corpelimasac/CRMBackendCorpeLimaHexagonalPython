from app.core.ports.services.generator_excel_port import ExcelGeneratorPort
from app.adapters.inbound.api.schemas.generar_oc_schemas import GenerarOCRequest
from app.core.ports.repositories.ordenes_compra_repository import OrdenesCompraRepositoryPort
from app.shared.serializers.generator_oc.generador import Generador
import os
import tempfile
from typing import Dict, Any

class OpenPyXLExcelGenerator(ExcelGeneratorPort):
    def __init__(self, ordenes_compra_repo: OrdenesCompraRepositoryPort):
        self.ordenes_compra_repo = ordenes_compra_repo

    def generate_for_order(self, request: GenerarOCRequest) -> Dict[str, bytes]:
        """
        Genera archivos Excel para cada contacto de proveedor y devuelve un diccionario
        con el nombre del archivo como clave y el contenido en bytes como valor.
        """
        excel_files = {}

        
        # Obtener información de la orden de compra
        resultados = self.ordenes_compra_repo.obtener_info_oc(request)

        print(f"Este es el resultado: {resultados}")
        
        if not resultados:
            return excel_files

        # Agrupar resultados por contacto de proveedor
        contactos_data = {}
        for resultado in resultados:
            id_contacto = resultado.IDPROVEEDORCONTACTO
            if id_contacto not in contactos_data:
                contactos_data[id_contacto] = []
            contactos_data[id_contacto].append(resultado)

        # Generar Excel para cada contacto
        for id_contacto, resultados_contacto in contactos_data.items():
            if not resultados_contacto:
                continue
                
            # Obtener datos del primer resultado para metadatos
            primer_resultado = resultados_contacto[0]
            nombre_proveedor = primer_resultado.PROVEEDOR or "Proveedor"
            igv = primer_resultado.IGV or "SIN IGV"
            numero_oc = primer_resultado.NUMERO_OC
            
            # Convertir resultados al formato esperado por Generador
            datos_para_excel = [
                {
                    'CANT': r.CANT,
                    'UMED': r.UMED, 
                    'PRODUCTO': r.PRODUCTO,
                    'MARCA': r.MARCA,
                    'MODELO': r.MODELO,
                    'P.UNIT': r.PUNIT,
                    'PROVEEDOR': r.PROVEEDOR,
                    'PERSONAL': r.PERSONAL,
                    'CELULAR': r.CELULAR,
                    'CORREO': r.CORREO,
                    'DIRECCION': r.DIRECCION,
                    'FECHA': r.FECHA,
                    'MONEDA': r.MONEDA,
                    'PAGO': r.PAGO
                } for r in resultados_contacto
            ]
            
            # Crear directorio temporal
            with tempfile.TemporaryDirectory() as temp_dir:
                generador = Generador(
                    num_orden=numero_oc,
                    oc=datos_para_excel,
                    proveedor=nombre_proveedor,
                    igv=igv,
                    output_folder=temp_dir,
                    consorcio=request.consorcio
                )
                generador.generar_excel()
                
                # Leer el archivo generado
                archivo_path = os.path.join(temp_dir, generador.output_file)
                if os.path.exists(archivo_path):
                    with open(archivo_path, 'rb') as f:
                        excel_files[generador.output_file] = f.read()

        return excel_files

    def generate_from_data(self, orden_data: Any, productos_data: list[Any], proveedor_data: Any, numero_oc: str, consorcio: bool = False) -> Dict[str, bytes]:
        """
        Genera archivos Excel a partir de datos directos sin consultar BD.

        Args:
            orden_data: Datos de la orden (moneda, pago, entrega, fecha)
            productos_data: Lista de productos con sus detalles
            proveedor_data: Datos del proveedor y contacto
            numero_oc: Número de la orden de compra
            consorcio: Si es consorcio

        Returns:
            Dict[str, bytes]: Diccionario con nombre de archivo y contenido en bytes
        """
        excel_files = {}

        # Determinar IGV del primer producto (asumimos que todos tienen el mismo)
        igv = productos_data[0].get('igv', 'SIN IGV') if productos_data else 'SIN IGV'

        # Convertir datos al formato esperado por Generador
        datos_para_excel = [
            {
                'CANT': p.get('cantidad'),
                'UMED': p.get('unidadMedida'),
                'PRODUCTO': p.get('producto'),
                'MARCA': p.get('marca'),
                'MODELO': p.get('modelo', ''),
                'P.UNIT': p.get('precioUnitario'),
                'PROVEEDOR': proveedor_data.get('razonSocial'),
                'PERSONAL': proveedor_data.get('nombreContacto'),
                'CELULAR': proveedor_data.get('celular', ''),
                'CORREO': proveedor_data.get('correo', ''),
                'DIRECCION': proveedor_data.get('direccion', ''),
                'FECHA': orden_data.get('fecha'),
                'MONEDA': orden_data.get('moneda'),
                'PAGO': orden_data.get('pago')
            } for p in productos_data
        ]

        # Crear directorio temporal
        with tempfile.TemporaryDirectory() as temp_dir:
            generador = Generador(
                num_orden=numero_oc,
                oc=datos_para_excel,
                proveedor=proveedor_data.get('razonSocial', 'Proveedor'),
                igv=igv,
                output_folder=temp_dir,
                consorcio=consorcio
            )
            generador.generar_excel()

            # Leer el archivo generado
            archivo_path = os.path.join(temp_dir, generador.output_file)
            if os.path.exists(archivo_path):
                with open(archivo_path, 'rb') as f:
                    excel_files[generador.output_file] = f.read()

        return excel_files
