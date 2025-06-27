import os
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.drawing.image import Image
from datetime import datetime

class Generador:
    def __init__(self, num_orden, oc, proveedor, igv, output_folder=None): 
        # Si no se especifica output_folder, usar la carpeta data dentro del mismo directorio
        if output_folder is None:
            # Obtener el directorio actual del archivo generador.py
            current_dir = os.path.dirname(os.path.abspath(__file__))
            output_folder = os.path.join(current_dir, "data")
        
        # Crear la carpeta de salida si no existe
        os.makedirs(output_folder, exist_ok=True)
        
        self.cabecera = {
            "B11": "Señores",
            "B12": "Atencion",
            "B13": "Telefono",
            "B14": "Correo",
            "B15": "Direccion",
            "F11": "Fecha",
            "F12": "Moneda",
            "F13": "Entrega",
            "F14": "Pago"
        }
        self.output_folder = output_folder
        self.orden = oc
        self.igv=igv
        
        # Configuración de la imagen
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.image_path = os.path.join(current_dir, "img", "principal.png")
        self.image_width = 300  # Ancho en píxeles
        self.image_height = 150  # Alto en píxeles
        self.image_position = "D1"  # Posición en Excel (ej: "D1")
        
        self.output_file = f"OC {num_orden}-{datetime.now().year} {proveedor}.xlsx"
        self.subTitle=f"ORDEN DE COMPRA N° {num_orden}-{datetime.now().year}"
        self.wb = Workbook()
        self.ws = self.wb.active
        self.last_product_row = None 

    def aplicar_estilo_fondo(self):
        white_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
        for row in self.ws.iter_rows(min_row=1, max_row=50, min_col=1, max_col=20):
            for cell in row:
                cell.fill = white_fill

    def configurar_ancho_columna(self, col_index, width):
        col_letter = get_column_letter(col_index)
        self.ws.column_dimensions[col_letter].width = width

    def agregar_header(self):
        for cell, value in self.cabecera.items():
            self.ws[cell] = value
            self.ws[cell].font = Font(bold=True)

    def agregar_cont_header(self):
        datos = self.orden[0]  # Usar el primer registro para rellenar los valores de la cabecera
        self.ws["C11"] = datos.get("PROVEEDOR", "")
        self.ws["C12"] = datos.get("PERSONAL", "")
        self.ws["C13"] = datos.get("CELULAR", "")
        self.ws["C14"] = datos.get("CORREO", "")
        self.ws["C15"] = datos.get("DIRECCION", "")
        self.ws["G11"] = datos.get("FECHA", "")
        self.ws["G12"] = datos.get("MONEDA", "")
        self.ws["G13"] = "INMEDIATO"
        self.ws["G14"] = datos.get("PAGO", "")
        self.ws["D8"] = self.subTitle
        self.ws["D8"].font = Font(bold=True)  
        self.ws["D8"].alignment = Alignment(horizontal="center")
# "F12": "Moneda",
#             "F13": "Entrega",
#             "F14": "Pago"

    def agregar_productos(self):
        encabezados = ["CANT", "UND", "PRODUCTO", "MARCA", "MODELO", "P.UNIT", "P.TOTAL"]
        start_row = 18  
        start_col = 2  

        double_side = Side(border_style="double", color="000000")

        for col_offset, encabezado in enumerate(encabezados):
            cell = self.ws.cell(row=start_row, column=start_col + col_offset)
            cell.value = encabezado
            cell.font = Font(bold=True)
            cell.border = Border(top=double_side, bottom=double_side)

        for idx, producto in enumerate(self.orden, start=1):
            row = start_row + idx
            self.ws.cell(row=row, column=2).value = producto.get("CANT", "")
            self.ws.cell(row=row, column=3).value = producto.get("UMED", "")
            self.ws.cell(row=row, column=4).value = producto.get("PRODUCTO", "")
            self.ws.cell(row=row, column=5).value = producto.get("MARCA", "")
            self.ws.cell(row=row, column=6).value = producto.get("MODELO", "")
            self.ws.cell(row=row, column=7).value = producto.get("P.UNIT", "")
            #self.ws.cell(row=row, column=8).value = producto.get("P.UNIT", "") * producto.get("CANT", "")
            self.ws.cell(row=row, column=8).value =f"=B{row}*G{row}"
            
        self.last_product_row = start_row + len(self.orden)

        if self.last_product_row > start_row:
            for col_offset in range(len(encabezados)):
                cell = self.ws.cell(row=self.last_product_row, column=start_col + col_offset)
                cell.border = Border(bottom=double_side)
    
    
    def agregar_total(self):

        if not self.last_product_row:
            self.last_product_row = 18
            
        total_row = self.last_product_row + 1
        total_formula_cell = self.ws.cell(row=total_row, column=8)
        total_formula_cell.value = f"=SUM(H18:H{self.last_product_row})"  # Fórmula Excel para sumar desde H18 a H última fila
        total_formula_cell.font = Font(bold=True)  # Aplicar negrita
        total_formula_cell.alignment = Alignment(horizontal="center")  # Centrar el texto
        
        if self.igv == 1:
            cell_igv = self.ws.cell(row=total_row+1, column=8)
            cell_igv.value = f"=H{total_row}*0.18"
            cell_igv.font = Font(bold=True)
            cell_igv.alignment = Alignment(horizontal="center")
            
            total_igv = self.ws.cell(row=total_row+2, column=8)
            total_igv.value= f"=SUM(H{total_row}:H{total_row+1})"
            total_igv.font = Font(bold=True)
            total_igv.alignment = Alignment(horizontal="center")     
            
            descripcion_cell = self.ws.cell(row=total_row, column=7)
            descripcion_cell.value = "P.UNITARIO:"
            descripcion_cell.font = Font(bold=True)
            descripcion_cell.alignment = Alignment(horizontal="right")
            
            descripcion_cell = self.ws.cell(row=total_row, column=7)
            descripcion_cell.value = "P.UNITARIO:"
            descripcion_cell.font = Font(bold=True)
            descripcion_cell.alignment = Alignment(horizontal="right")
            
            descripcion_cell = self.ws.cell(row=total_row+1, column=7)
            descripcion_cell.value = "IGV:"
            descripcion_cell.font = Font(bold=True)
            descripcion_cell.alignment = Alignment(horizontal="right")    

            descripcion_cell = self.ws.cell(row=total_row+2, column=7)
            descripcion_cell.value = "TOTAL:"
            descripcion_cell.font = Font(bold=True)
            descripcion_cell.alignment = Alignment(horizontal="right")  
            descripcion_cell.border=Border(top=Side(style='thin'))  
        else:
            descripcion_cell = self.ws.cell(row=total_row, column=7)
            descripcion_cell.value = "TOTAL:"
            descripcion_cell.font = Font(bold=True)
            descripcion_cell.alignment = Alignment(horizontal="right")          

        
    def agregar_footer(self):
        if not self.last_product_row:
            self.last_product_row = 18

        info_start_row = self.last_product_row + 4  

        info_lines = [
            "FACTURAR:",
            "CORPELIMA S.A.C",
            "RUC: 20601460913",
            "CALLE  55 MZ WW2 LT 13   URB. LA FLORESTA DE PRO   LOS OLIVOS  LIMA",
            "",
            "BCP:   CTA. CTE  DOLARES  No    1942383846160",
            "BCP:   CTA. CTE SOLES     No    1942395668064",
            "",
            "CEL:  952531238",
            "ventas@corpelima.com"
        ]

        for i, line in enumerate(info_lines):
            row = info_start_row + i
            self.ws.cell(row=row, column=4).value = line

    def agregar_imagen(self):
        """
        Agrega la imagen al Excel con el tamaño y posición especificados
        """
        try:
            img = Image(self.image_path)
            
            # Configurar el tamaño de la imagen si se especifica
            if self.image_width and self.image_height:
                # Convertir píxeles a puntos (1 píxel ≈ 0.75 puntos)
                width_pt = self.image_width * 1.80
                height_pt = self.image_height * 0.75
                img.width = width_pt
                img.height = height_pt
                print(f"Imagen configurada con tamaño: {self.image_width}x{self.image_height} píxeles ({width_pt:.1f}x{height_pt:.1f} puntos)")
            elif self.image_width:
                # Solo ancho especificado, mantener proporción
                width_pt = self.image_width * 0.75
                img.width = width_pt
                print(f"Imagen configurada con ancho: {self.image_width} píxeles ({width_pt:.1f} puntos)")
            elif self.image_height:
                # Solo alto especificado, mantener proporción
                height_pt = self.image_height * 0.75
                img.height = height_pt
                print(f"Imagen configurada con alto: {self.image_height} píxeles ({height_pt:.1f} puntos)")
            else:
                # Tamaño por defecto (pequeño)
                img.width = 150  # 200 píxeles
                img.height = 75  # 100 píxeles
                print("Imagen configurada con tamaño por defecto: 200x100 píxeles")
            
            # Agregar la imagen en la posición especificada
            self.ws.add_image(img, self.image_position)
            print(f"Imagen agregada en posición: {self.image_position}")
            
        except Exception as e:
            print(f"Advertencia: No se pudo cargar la imagen {self.image_path}: {e}")

    def guardar_archivo(self):
        full_path = os.path.join(self.output_folder, self.output_file)
        self.wb.save(full_path)
        print(f"Archivo '{self.output_file}' creado con éxito en: {full_path}")

    def generar_excel(self):
        self.aplicar_estilo_fondo()
        self.configurar_ancho_columna(4, 75)
        self.agregar_header()
        self.agregar_cont_header()
        self.agregar_productos()
        self.agregar_total()  
        self.agregar_footer()
        self.agregar_imagen()
        self.guardar_archivo()