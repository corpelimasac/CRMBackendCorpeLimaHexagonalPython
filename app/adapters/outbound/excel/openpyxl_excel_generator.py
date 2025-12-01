"""
Generador de archivos Excel para órdenes de compra usando OpenPyXL.

Implementa el puerto ExcelGeneratorPort usando la librería OpenPyXL.
"""
from typing import Dict, List
import os
import tempfile
from decimal import Decimal

from app.core.ports.services.generator_excel_port import ExcelGeneratorPort
from app.core.ports.repositories.ordenes_compra_repository import OrdenesCompraRepositoryPort
from app.core.domain.dtos.orden_compra_dtos import (
    ObtenerInfoOCQuery,
    DatosExcelOC,
    DatosOrdenExcel,
    DatosProveedorExcel,
    DatosProductoExcel,
)
from app.shared.serializers.generator_oc.generador import Generador


class OpenPyXLExcelGenerator(ExcelGeneratorPort):
    """
    Generador de Excel usando OpenPyXL.

    Responsabilidad: Generar archivos Excel de órdenes de compra
    manteniendo la lógica de archivos temporales intacta.
    """

    def __init__(self, ordenes_compra_repo: OrdenesCompraRepositoryPort):
        self.ordenes_compra_repo = ordenes_compra_repo

    def generate_for_order(self, query: ObtenerInfoOCQuery) -> Dict[str, bytes]:
        """
        Genera archivos Excel para cada contacto de proveedor.

        LÓGICA TEMPORAL INTACTA: Usa tempfile.TemporaryDirectory para
        guardar archivos temporalmente.

        Args:
            query: Query del dominio con los criterios para generar OC

        Returns:
            Dict[str, bytes]: Diccionario con nombre de archivo y contenido en bytes
        """
        excel_files = {}

        # Obtener información de la orden de compra (ahora retorna List[DatosExcelOC])
        resultados: List[DatosExcelOC] = self.ordenes_compra_repo.obtener_info_oc(query)

        print(f"Este es el resultado: {resultados}")

        if not resultados:
            return excel_files

        # Agrupar resultados por contacto de proveedor
        contactos_data = {}
        for resultado in resultados:
            id_contacto = resultado.id_proveedor_contacto
            if id_contacto not in contactos_data:
                contactos_data[id_contacto] = []
            contactos_data[id_contacto].append(resultado)

        # Generar Excel para cada contacto
        for id_contacto, resultados_contacto in contactos_data.items():
            if not resultados_contacto:
                continue

            # Obtener datos del primer resultado para metadatos
            primer_resultado = resultados_contacto[0]
            nombre_proveedor = primer_resultado.proveedor or "Proveedor"
            numero_oc = primer_resultado.numero_oc

            # Determinar IGV: verificar todos los resultados para determinar si hay mezcla
            tipos_igv_resultados = set()
            for r in resultados_contacto:
                igv_resultado = (r.igv or '').upper()
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
                print(f"[EXCEL GENERATOR] TODOS SIN IGV - Excel mostrará desglose de IGV")
                for r in resultados_contacto:
                    datos_para_excel.append({
                        'CANT': r.cantidad,
                        'UMED': r.unidad_medida,
                        'PRODUCTO': r.producto,
                        'MARCA': r.marca,
                        'MODELO': r.modelo,
                        'P.UNIT': float(r.precio_unitario),  # Precio sin modificar
                        'PROVEEDOR': r.proveedor,
                        'PERSONAL': r.personal,
                        'CELULAR': r.celular,
                        'CORREO': r.correo,
                        'DIRECCION': r.direccion,
                        'FECHA': r.fecha,
                        'MONEDA': r.moneda,
                        'PAGO': r.pago
                    })

            elif mixtos:
                # CASO 2: MIXTOS - Uniformizar solo los SIN IGV, Excel mostrará solo TOTAL
                igv = 'CON IGV'
                print(f"[EXCEL GENERATOR] MIXTOS - Uniformizando productos SIN IGV")
                for r in resultados_contacto:
                    igv_producto = (r.igv or '').upper()
                    precio_unitario = float(r.precio_unitario)

                    if igv_producto == 'SIN IGV':
                        precio_unitario = round(float(r.precio_unitario) * 1.18, 2)
                        print(f"[EXCEL] Producto '{r.producto}' SIN IGV uniformizado: {r.precio_unitario} → {precio_unitario}")

                    datos_para_excel.append({
                        'CANT': r.cantidad,
                        'UMED': r.unidad_medida,
                        'PRODUCTO': r.producto,
                        'MARCA': r.marca,
                        'MODELO': r.modelo,
                        'P.UNIT': precio_unitario,
                        'PROVEEDOR': r.proveedor,
                        'PERSONAL': r.personal,
                        'CELULAR': r.celular,
                        'CORREO': r.correo,
                        'DIRECCION': r.direccion,
                        'FECHA': r.fecha,
                        'MONEDA': r.moneda,
                        'PAGO': r.pago
                    })

            else:
                # CASO 3: TODOS CON IGV - No modificar nada, Excel mostrará solo TOTAL
                igv = 'CON IGV'
                print(f"[EXCEL GENERATOR] TODOS CON IGV - Sin modificaciones")
                for r in resultados_contacto:
                    datos_para_excel.append({
                        'CANT': r.cantidad,
                        'UMED': r.unidad_medida,
                        'PRODUCTO': r.producto,
                        'MARCA': r.marca,
                        'MODELO': r.modelo,
                        'P.UNIT': float(r.precio_unitario),
                        'PROVEEDOR': r.proveedor,
                        'PERSONAL': r.personal,
                        'CELULAR': r.celular,
                        'CORREO': r.correo,
                        'DIRECCION': r.direccion,
                        'FECHA': r.fecha,
                        'MONEDA': r.moneda,
                        'PAGO': r.pago
                    })

            print(f"[EXCEL GENERATOR] Contacto {id_contacto} - IGV para Excel: {igv}")

            # === LÓGICA TEMPORAL INTACTA: Crear directorio temporal ===
            with tempfile.TemporaryDirectory() as temp_dir:
                generador = Generador(
                    num_orden=numero_oc,
                    oc=datos_para_excel,
                    proveedor=nombre_proveedor,
                    igv=igv,
                    output_folder=temp_dir,
                    consorcio=query.consorcio
                )
                generador.generar_excel()

                # Leer el archivo generado del directorio temporal
                archivo_path = os.path.join(temp_dir, generador.output_file)
                if os.path.exists(archivo_path):
                    with open(archivo_path, 'rb') as f:
                        excel_files[generador.output_file] = f.read()

        return excel_files

    def generate_from_data(
        self,
        orden_data: DatosOrdenExcel,
        productos_data: List[DatosProductoExcel],
        proveedor_data: DatosProveedorExcel,
        numero_oc: str,
        consorcio: bool = False
    ) -> Dict[str, bytes]:
        """
        Genera archivos Excel a partir de datos directos sin consultar BD.

        LÓGICA TEMPORAL INTACTA: Usa tempfile.TemporaryDirectory para
        guardar archivos temporalmente.

        Args:
            orden_data: Datos de la orden (fecha, moneda, pago, entrega)
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
            igv_producto = (p.igv or '').upper()
            if igv_producto:
                tipos_igv_productos.add(igv_producto)

        print(f"[EXCEL GENERATOR] Tipos de IGV encontrados en productos: {tipos_igv_productos}")

        # Determinar la estrategia según los tipos de IGV
        todos_sin_igv = tipos_igv_productos == {'SIN IGV'}
        todos_con_igv = tipos_igv_productos == {'CON IGV'} or len(tipos_igv_productos) == 0
        mixtos = len(tipos_igv_productos) > 1

        # Procesar productos según la estrategia
        productos_data_uniformizados: List[DatosProductoExcel] = []

        if todos_sin_igv:
            # CASO 1: TODOS SIN IGV - No uniformizar, el Excel mostrará SUBTOTAL + IGV + TOTAL
            igv = 'SIN IGV'
            print(f"[EXCEL GENERATOR] TODOS SIN IGV - Excel mostrará desglose de IGV")
            productos_data_uniformizados = list(productos_data)  # Copiar lista

        elif mixtos:
            # CASO 2: MIXTOS - Uniformizar solo los SIN IGV, Excel mostrará solo TOTAL
            igv = 'CON IGV'
            print(f"[EXCEL GENERATOR] MIXTOS - Uniformizando productos SIN IGV")
            for p in productos_data:
                igv_producto = (p.igv or '').upper()

                if igv_producto == 'SIN IGV':
                    precio_sin_igv = p.precio_unitario
                    precio_con_igv = Decimal(str(round(float(precio_sin_igv) * 1.18, 2)))
                    # Crear nuevo DTO con precio uniformizado
                    producto_uniformizado = DatosProductoExcel(
                        cantidad=p.cantidad,
                        unidad_medida=p.unidad_medida,
                        producto=p.producto,
                        marca=p.marca,
                        modelo=p.modelo,
                        precio_unitario=precio_con_igv,
                        igv='CON IGV'
                    )
                    print(f"[EXCEL] Producto SIN IGV uniformizado: {precio_sin_igv} → {precio_con_igv}")
                    productos_data_uniformizados.append(producto_uniformizado)
                else:
                    productos_data_uniformizados.append(p)

        else:
            # CASO 3: TODOS CON IGV - No modificar nada, Excel mostrará solo TOTAL
            igv = 'CON IGV'
            print(f"[EXCEL GENERATOR] TODOS CON IGV - Sin modificaciones")
            productos_data_uniformizados = list(productos_data)  # Copiar lista

        print(f"[EXCEL GENERATOR] IGV para Excel: {igv}")

        # Convertir datos al formato esperado por Generador (usando productos uniformizados)
        datos_para_excel = [
            {
                'CANT': p.cantidad,
                'UMED': p.unidad_medida,
                'PRODUCTO': p.producto,
                'MARCA': p.marca,
                'MODELO': p.modelo or '',
                'P.UNIT': float(p.precio_unitario),
                'PROVEEDOR': proveedor_data.razon_social,
                'PERSONAL': proveedor_data.nombre_contacto,
                'CELULAR': proveedor_data.celular or '',
                'CORREO': proveedor_data.correo or '',
                'DIRECCION': proveedor_data.direccion or '',
                'FECHA': orden_data.fecha,
                'MONEDA': orden_data.moneda,
                'PAGO': orden_data.pago
            } for p in productos_data_uniformizados
        ]

        # === LÓGICA TEMPORAL INTACTA: Crear directorio temporal ===
        with tempfile.TemporaryDirectory() as temp_dir:
            generador = Generador(
                num_orden=numero_oc,
                oc=datos_para_excel,
                proveedor=proveedor_data.razon_social,
                igv=igv,
                output_folder=temp_dir,
                consorcio=consorcio
            )
            generador.generar_excel()

            # Leer el archivo generado del directorio temporal
            archivo_path = os.path.join(temp_dir, generador.output_file)
            if os.path.exists(archivo_path):
                with open(archivo_path, 'rb') as f:
                    excel_files[generador.output_file] = f.read()

        return excel_files
