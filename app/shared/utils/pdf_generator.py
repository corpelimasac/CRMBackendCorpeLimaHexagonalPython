"""
Generador de PDF para cartas de garantía
"""

class CartaGarantiaGenerator:
    """
    Generador de cartas de garantía en formato PDF
    """
    
    def generate_pdf(self, registration_name: str, num_coti: str, fact: str, detalles: list, date: str) -> bytes:
        """
        Generar PDF de carta de garantía
        
        Args:
            registration_name: Nombre del cliente
            num_coti: Número de cotización
            fact: Número de factura
            detalles: Lista de detalles de productos
            date: Fecha formateada
            
        Returns:
            bytes: Contenido del PDF en bytes
        """
        # Esta es una implementación básica
        # En una implementación real, usarían una librería como ReportLab o similares
        try:
            # Simulación de generación de PDF
            pdf_content = f"""
            CARTA DE GARANTÍA
            =================
            
            Cliente: {registration_name}
            Cotización: {num_coti}
            Factura: {fact}
            Fecha: {date}
            
            Detalles de productos:
            """
            
            for i, (cant, und, desc) in enumerate(detalles, 1):
                pdf_content += f"\n{i}. Cantidad: {cant}, Unidad: {und}, Descripción: {desc}"
            
            # Convertir a bytes (en un caso real, esto sería un PDF real)
            return pdf_content.encode('utf-8')
            
        except Exception as e:
            raise Exception(f"Error generando PDF: {str(e)}")
    
    def _get_pdf_template(self) -> str:
        """
        Obtener plantilla base para el PDF
        """
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Carta de Garantía</title>
            <style>
                body { font-family: Arial, sans-serif; }
                .header { text-align: center; margin-bottom: 30px; }
                .content { margin: 20px; }
                .details { margin-top: 20px; }
                table { width: 100%; border-collapse: collapse; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>CARTA DE GARANTÍA</h1>
            </div>
            <div class="content">
                <!-- Contenido dinámico -->
            </div>
        </body>
        </html>
        """ 