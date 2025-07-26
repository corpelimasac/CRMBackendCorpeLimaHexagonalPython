from app.core.ports.services.invoice_processor_port import InvoiceProcessorPort
from app.shared.utils.xml_processor import InvoiceExtractor
from app.shared.serializers.pdf_generator.pdf_convert import generate_pdf

class XmlToPdfProcessorAdapter(InvoiceProcessorPort):
    def process_to_pdf(self, xml_file_path: str) -> tuple[bytes, str]:
        # Aquí va la lógica de tu servicio original
        extractor = InvoiceExtractor(xml_file_path)
        extractor.extract_data()
        
        registration_name, num_coti, fact, detalles, date, nombre_pdf = extractor.get_data()

        pdf_bytes = generate_pdf(
            cliente=registration_name,
            fecha=date,
            numero_factura=fact,
            productos=detalles,
            numero_cotizacion=num_coti,
            nombre_pdf=nombre_pdf
        )
        return pdf_bytes, nombre_pdf