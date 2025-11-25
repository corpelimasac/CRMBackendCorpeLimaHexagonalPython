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
            numero_oc = primer_resultado.NUMERO_OC

            # Determinar IGV: verificar todos los resultados para determinar si hay mezcla
            tipos_igv_resultados = set()
            for r in resultados_contacto:
                igv_resultado = (r.IGV or '').upper()
                if igv_resultado:
                    tipos_igv_resultados.add(igv_resultado)

            print(f"[EXCEL GENERATOR] Contacto {id_contacto} - Tipos de IGV en BD: {tipos_igv_resultados}")

            # Determinar la estrategia según los tipos de IGV
            todos_sin_igv = tipos_igv_resultados == {'SIN IGV'}
            todos_con_igv = tipos_igv_resultados == {'CON IGV'} or len(tipos_igv_resultados) == 0
            mixtos = len(tipos_igv_resultados) > 1

            # Convertir resultados al formato esperado por Generador
            datos_para_excel = []

            if todos_sin_igv:
                # CASO 1: TODOS SIN IGV - No uniformizar, el Excel mostrará SUBTOTAL + IGV + TOTAL
                igv = 'SIN IGV'
                print(f" [EXCEL GENERATOR] TODOS SIN IGV - Excel mostrará desglose de IGV ")
                for r in resultados_contacto:
                    datos_para_excel.append({
                        'CANT': r.CANT,
                        'UMED': r.UMED,
                        'PRODUCTO': r.PRODUCTO,
                        'MARCA': r.MARCA,
                        'MODELO': r.MODELO,
                        'P.UNIT': r.PUNIT,  # Precio sin modificar
                        'PROVEEDOR': r.PROVEEDOR,
                        'PERSONAL': r.PERSONAL,
                        'CELULAR': r.CELULAR,
                        'CORREO': r.CORREO,
                        'DIRECCION': r.DIRECCION,
                        'FECHA': r.FECHA,
                        'MONEDA': r.MONEDA,
                        'PAGO': r.PAGO
                    })

            elif mixtos:
                # CASO 2: MIXTOS - Uniformizar solo los SIN IGV, Excel mostrará solo TOTAL
                igv = 'CON IGV'
                print(f"[EXCEL GENERATOR] MIXTOS - Uniformizando productos SIN IGV")
                for r in resultados_contacto:
                    igv_producto = (r.IGV or '').upper()
                    precio_unitario = r.PUNIT

                    if igv_producto == 'SIN IGV':
                        precio_unitario = round(r.PUNIT * 1.18, 2)
                        print(f"[EXCEL] Producto '{r.PRODUCTO}' SIN IGV uniformizado: {r.PUNIT} → {precio_unitario}")

                    datos_para_excel.append({
                        'CANT': r.CANT,
                        'UMED': r.UMED,
                        'PRODUCTO': r.PRODUCTO,
                        'MARCA': r.MARCA,
                        'MODELO': r.MODELO,
                        'P.UNIT': precio_unitario,
                        'PROVEEDOR': r.PROVEEDOR,
                        'PERSONAL': r.PERSONAL,
                        'CELULAR': r.CELULAR,
                        'CORREO': r.CORREO,
                        'DIRECCION': r.DIRECCION,
                        'FECHA': r.FECHA,
                        'MONEDA': r.MONEDA,
                        'PAGO': r.PAGO
                    })

            else:
                # CASO 3: TODOS CON IGV - No modificar nada, Excel mostrará solo TOTAL
                igv = 'CON IGV'
                print(f"[EXCEL GENERATOR] TODOS CON IGV - Sin modificaciones")
                for r in resultados_contacto:
                    datos_para_excel.append({
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
                    })

            print(f"[EXCEL GENERATOR] Contacto {id_contacto} - IGV para Excel: {igv}")
            
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

        # Determinar IGV: verificar todos los productos para determinar si hay mezcla
        tipos_igv_productos = set()
        for p in productos_data:
            igv_producto = p.get('igv', '').upper()
            if igv_producto:
                tipos_igv_productos.add(igv_producto)

        print(f"[EXCEL GENERATOR] Tipos de IGV encontrados en productos: {tipos_igv_productos}")

        # Determinar la estrategia según los tipos de IGV
        todos_sin_igv = tipos_igv_productos == {'SIN IGV'}
        todos_con_igv = tipos_igv_productos == {'CON IGV'} or len(tipos_igv_productos) == 0
        mixtos = len(tipos_igv_productos) > 1

        # Procesar productos según la estrategia
        productos_data_uniformizados = []

        if todos_sin_igv:
            # CASO 1: TODOS SIN IGV - No uniformizar, el Excel mostrará SUBTOTAL + IGV + TOTAL
            igv = 'SIN IGV'
            print(f"[EXCEL GENERATOR] TODOS SIN IGV - Excel mostrará desglose de IGV")
            productos_data_uniformizados = [p.copy() for p in productos_data]

        elif mixtos:
            # CASO 2: MIXTOS - Uniformizar solo los SIN IGV, Excel mostrará solo TOTAL
            igv = 'CON IGV'
            print(f"[EXCEL GENERATOR] MIXTOS - Uniformizando productos SIN IGV")
            for p in productos_data:
                producto = p.copy()
                igv_producto = producto.get('igv', '').upper()

                if igv_producto == 'SIN IGV':
                    precio_sin_igv = producto.get('precioUnitario', 0)
                    precio_con_igv = round(precio_sin_igv * 1.18, 2)
                    producto['precioUnitario'] = precio_con_igv
                    producto['igv'] = 'CON IGV'
                    print(f"[EXCEL] Producto SIN IGV uniformizado: {precio_sin_igv} → {precio_con_igv}")

                productos_data_uniformizados.append(producto)

        else:
            # CASO 3: TODOS CON IGV - No modificar nada, Excel mostrará solo TOTAL
            igv = 'CON IGV'
            print(f"[EXCEL GENERATOR] TODOS CON IGV - Sin modificaciones")
            productos_data_uniformizados = [p.copy() for p in productos_data]

        print(f"[EXCEL GENERATOR] IGV para Excel: {igv}")

        # Convertir datos al formato esperado por Generador (usando productos uniformizados)
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
            } for p in productos_data_uniformizados
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
