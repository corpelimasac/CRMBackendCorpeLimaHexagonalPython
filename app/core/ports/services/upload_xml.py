import os
from fastapi import UploadFile, HTTPException
from app.shared.utils.xml_processor import InvoiceExtractor  #importar el extractor de datos del XML
from app.shared.serializers.pdf_generator.pdf_convert import generate_pdf  #importar el generador de PDF

class UploadXmlService:
    """Servicio para manejar la lógica de negocio de UploadXml"""

    @staticmethod
    async def upload_xml(xml_file: UploadFile):
        """Subir un archivo XML y transformarlo a PDF"""
        if not xml_file or not xml_file.filename:
            raise HTTPException(status_code=400, detail="No se ha subido ningún archivo")
        
        if not xml_file.filename.lower().endswith('.xml'):
            raise HTTPException(status_code=400, detail="El archivo debe tener extensión .xml")
        
        # Crear carpeta files si no existe
        files_dir = "./app/shared/serializers/pdf_generator/files"
        os.makedirs(files_dir, exist_ok=True)
        
        # Ruta temporal para guardar el XML
        xml_path = os.path.join(files_dir, xml_file.filename)
        pdf_path=None
        
        try:
            # Guardar el archivo XML temporalmente
            with open(xml_path, "wb") as buffer:
                content = await xml_file.read()
                buffer.write(content)

            # Extraer datos del XML
            invoice_extractor = InvoiceExtractor(xml_path)
            invoice_extractor.extract_data()

            registration_name, num_coti, fact, detalles, date, nombre_pdf = invoice_extractor.get_data()

            # Generar el PDF con los datos extraídos
            pdf_data = generate_pdf(
                cliente=registration_name,
                fecha=date,
                numero_factura=fact,
                productos=detalles,
                numero_cotizacion=num_coti,
                nombre_pdf=nombre_pdf
            )
            
            pdf_path=os.path.join(files_dir, nombre_pdf)

            print(f"PDF generado: {nombre_pdf}")
           

            return pdf_data, nombre_pdf
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error al procesar el archivo XML: {str(e)}"
            )
        finally:
            #Eliminar el archivo XML temporal después del procesamiento
            if os.path.exists(xml_path):
                try:
                    os.remove(xml_path)
                except Exception as e:
                    print(f"Advertencia: No se pudo eliminar el archivo temporal {xml_path}: {e}")
            
            if os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                except Exception as e:
                    print(f"Advertencia: No se pudo eliminar el archivo temporal {pdf_path}: {e}")
