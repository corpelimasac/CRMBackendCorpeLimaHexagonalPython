from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import StreamingResponse
from app.core.ports.services.upload_xml import UploadXmlService
import io
from urllib.parse import quote

# Configuración de la API
router = APIRouter(
    prefix="/upload-xml", 
    tags=["Upload XML"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", summary="Sube un XML y devuelve un PDF")
async def upload_xml(xml: UploadFile = File(...)):
    """
    Sube un archivo XML, extrae los datos y genera un PDF de carta de garantía
    
    - **xml**: Archivo XML a procesar
    
    Retorna un PDF descargable con la carta de garantía generada
    """
    try:
        # Validación adicional en el controlador
        if not xml.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="No se ha proporcionado un archivo"
            )
        
        if not xml.filename.lower().endswith(".xml"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="El archivo debe tener extensión .xml"
            )

        # Procesar el XML y generar el PDF
        pdf_bytes, pdf_name = await UploadXmlService.upload_xml(xml)

        # Codificar el nombre del archivo para URL
        encoded_filename = quote(pdf_name)

        # Usar el formato estándar para nombres con espacios/caracteres especiales
        headers = {
        "Content-Disposition": f"attachment; filename=\"{pdf_name}\"; filename*=UTF-8''{encoded_filename}"
        }

        print(headers)

        # Retornar el PDF como respuesta de descarga
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers=headers
        )
        
    except HTTPException:
        # Re-lanzar HTTPExceptions del servicio
        raise
    except Exception as e:
        # Capturar cualquier otro error inesperado
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
