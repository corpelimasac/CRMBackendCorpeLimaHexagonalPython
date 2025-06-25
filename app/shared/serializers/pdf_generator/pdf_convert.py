from app.shared.serializers.pdf_generator.carta_garantia import CartaGarantia

# Función para generar el PDF utilizando los datos extraídos
def generate_pdf(cliente, fecha, numero_factura, productos, numero_cotizacion, nombre_pdf):
    carta = CartaGarantia(cliente, fecha, numero_factura, productos, numero_cotizacion, nombre_pdf)
    carta.crear_pdf()  

    # Leer el PDF generado y devolverlo como respuesta
    with open(carta.nombre_pdf, 'rb') as pdf_file:
        return pdf_file.read()