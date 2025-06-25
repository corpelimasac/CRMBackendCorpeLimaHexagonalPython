from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pathlib import Path

class CartaGarantia:

    BASE_DIR = Path(__file__).resolve().parent
    
    def __init__(self, cliente, fecha, numero_factura, productos, numero_cotizacion, nombre_pdf):
        # Atributos que se usarán en el PDF
        self.cliente = cliente
        self.fecha = fecha
        self.numero_factura = numero_factura
        self.productos = productos
        self.numero_cotizacion = numero_cotizacion
        self.nombre_pdf = f"{self.BASE_DIR}/files/{nombre_pdf}"
        self.header_image = f"{self.BASE_DIR}/img/corpe_head.png" 
        self.sello_image = f"{self.BASE_DIR}/img/sello.png" 

    def dividir_texto(self, texto, max_longitud):
        """Función para dividir el texto largo en partes de longitud máxima"""
        return [texto[i:i + max_longitud] for i in range(0, len(texto), max_longitud)]

    def crear_pdf(self):
        # Crear el canvas
        c = canvas.Canvas(self.nombre_pdf, pagesize=letter)
        # ESTABLECER METADATOS
        c.setTitle(f"Carta de Garantía {self.cliente}")
        c.setAuthor("Corp Eléctrica")
        c.setSubject(f"Carta de Garantía {self.cliente}")
        c.setKeywords(f"Carta de Garantía, productos eléctricos, Corp Eléctrica")

        width, height = letter  # Tamaño de la página

        # --- HEADER ---
        header_image_width = 180  # Ajustar el ancho de la imagen
        header_image_height = 60  # Ajustar el alto de la imagen
        header_x = (width - header_image_width) / 2  # Centrar horizontalmente
        header_y = height - 80  # Posición desde el borde superior
        c.drawImage(self.header_image, header_x, header_y, header_image_width, header_image_height)

        # --- FOOTER ---
        footer_text = "Calle 55 Mzna WW2 Lote 13 Urb.Pro, La Floresta, Los Olivos| +51901664250 | corpelima@gmail.com - ventas@corpelima.com"
        footer_x = width / 2  # Centrar horizontalmente
        footer_y = 30  # Posición desde el borde inferior
        c.setFont("Helvetica", 10)  # Fuente y tamaño
        c.drawCentredString(footer_x, footer_y, footer_text)

        sello_image_width = 120
        sello_image_height = 120
        sello_x = (width - sello_image_width) / 2  # Centrar horizontalmente
        sello_y = 80  # Posición del sello en la página
        sello_y_1 = (height - sello_image_width) / 2

        # --- CONTENIDO ---
        text_x = 50  # Margen izquierdo
        text_y = height - 100  # Posición inicial del contenido

        # Fecha centrada a la derecha y en negrita
        c.setFont("Helvetica-Bold", 12)
        c.drawRightString(width - 50, height - 100, f"Lima, {self.fecha}")

        # Título "CARTA DE GARANTÍA" en negrita
        text_y -= 40
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, text_y, "CARTA DE GARANTÍA")

        # Cuerpo del texto
        text_y -= 30
        c.setFont("Helvetica", 12)
        content = [
            "Señores:",
            self.cliente,
            "",
            f"Nos es grato dirigirnos a Uds., para agradecerles su preferencia por la adquisición de los",
            f"Materiales Eléctricos, según Factura {self.numero_factura}.",
            "La presente tiene por finalidad GARANTIZAR la calidad de los Materiales atendidos, los",
            "cuales son Nuevos, Originales y Cumplen con las características expresadas en nuestras",
            "fichas técnicas.",
            "",
            "Detalle de productos:"
        ]

        # Dividir el nombre del cliente si es demasiado largo
        cliente_dividido = self.dividir_texto(self.cliente, 60)

        # Mostrar cada línea del contenido
        for line in content:
            if text_y <= 50:  # Si se queda sin espacio, hacer un salto de página
                c.showPage()
                # Dibujar header y footer en la nueva página
                c.drawImage(self.header_image, header_x, header_y, header_image_width, header_image_height)
                c.drawCentredString(footer_x, footer_y, footer_text)
                text_y = height - 100  # Reiniciar posición vertical

            if self.cliente in line:
                c.setFont("Helvetica-Bold", 12)
                for sub_line in cliente_dividido:
                    c.drawString(text_x, text_y, sub_line)
                    text_y -= 18  # Espaciado entre líneas actualizado
            else:
                c.setFont("Helvetica", 12)
                c.drawString(text_x, text_y, line)
                text_y -= 18  # Espaciado entre líneas actualizado

        # --- DETALLE DE PRODUCTOS ---
        for producto in self.productos:
            if text_y <= 50:  # Si no hay espacio suficiente, hacer salto de página
                c.showPage()
                # Dibujar header y footer en la nueva página
                c.drawImage(self.header_image, header_x, header_y, header_image_width, header_image_height, mask='auto')
                c.setFont("Helvetica", 10)
                c.drawCentredString(footer_x, footer_y, footer_text)

                text_y = height - 100  # Reiniciar posición vertical
            # Ajustar el texto de cada producto
            producto_text = f"- {producto[0]}  {producto[1]} - {producto[2]}"
            c.setFont("Helvetica", 10)

            # Si el texto es muy largo, se divide en varias líneas
            max_length = 80  # Limite de caracteres por línea
            if len(producto_text) > max_length:
                # Dividir el texto largo
                parts = [producto_text[i:i + max_length] for i in range(0, len(producto_text), max_length)]
                for part in parts:
                    c.drawString(text_x, text_y, part)
                    text_y -= 18  # Espaciado entre líneas actualizado
            else:
                c.drawString(text_x, text_y, producto_text)
                text_y -= 18  # Espaciado entre líneas actualizado

        # --- CONTINUACIÓN DEL CONTENIDO ---
        remaining_content = [
            "",
            "La presente Carta de Garantía es por el plazo de 1 años desde la emisión de la Factura.",
            "Esta Garantía es contra defectos de diseño o fabricación y no así por mal uso o instalación",
            "inadecuada.",
            "Queremos que consideren a nuestra Empresa como colaboradora constante de vuestros",
            "proyectos brindándoles siempre la mejor calidad en nuestros materiales.",
            "",
            f"Referencia: {self.numero_cotizacion}"
        ]

        for line in remaining_content:
            if text_y <= 50:  # Si se queda sin espacio, hacer un salto de página
                c.showPage()
                # Dibujar header y footer en la nueva página
                c.drawImage(self.header_image, header_x, header_y, header_image_width, header_image_height)
                c.setFont("Helvetica", 10)
                c.drawCentredString(footer_x, footer_y, footer_text)
                text_y = height - 100  # Reiniciar posición vertical
            # Negrita para la línea específica
            if "La presente Carta de Garantía es por el plazo de 2 años desde la emisión de la Factura." in line:
                c.setFont("Helvetica-Bold", 12)
            elif f" {self.numero_cotizacion}" in line:
                c.setFont("Helvetica-Bold", 12)
            else:
                c.setFont("Helvetica", 12)

            c.drawString(text_x, text_y, line)
            text_y -= 18  # Espaciado entre líneas actualizado

        # --- AGREGAR EL SELLO EN LA ÚLTIMA PÁGINA O NUEVA PÁGINA ---
        if text_y <= sello_image_height:  
            c.showPage()  
            # Dibujar el sello
            c.drawImage(self.sello_image, sello_x, sello_y, sello_image_width, sello_image_height)
            c.drawImage(self.header_image, header_x, header_y, header_image_width, header_image_height)
            c.setFont("Helvetica", 10)
            c.drawCentredString(footer_x, footer_y, footer_text)
            text_y = height - 100  # Reiniciar posición vertical
        else:
            c.drawImage(self.sello_image, sello_x, sello_y, sello_image_width, sello_image_height)

        # Guardar el PDF
        c.save()
