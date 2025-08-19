from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.core.use_cases.upload_invoice_use_case import UploadInvoiceUseCase
from app.dependencies import get_upload_invoice_use_case

router = APIRouter(prefix="/carta-garantia",
                    tags=["Generar Carta Garantia"], 
                    responses={404: {"description": "Not found"}})

@router.post("/generar")
async def upload_xml_endpoint(
    use_case: UploadInvoiceUseCase = Depends(get_upload_invoice_use_case),
    xml_file: UploadFile = File(...)
):
    if not xml_file.filename or not xml_file.filename.lower().endswith('.xml'):
        raise HTTPException(status_code=400, detail="El archivo debe ser un .xml válido.")
        
    xml_content = await xml_file.read() 
    
    try:
        pdf_bytes, pdf_filename = await use_case.execute(xml_content, xml_file.filename)
        
        headers = {'Content-Disposition': f'attachment; filename="{pdf_filename}"'}
        return StreamingResponse(iter([pdf_bytes]), media_type="application/pdf", headers=headers)
        
    except Exception as e:
        # Puedes manejar excepciones más específicas del dominio aquí
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {e}")