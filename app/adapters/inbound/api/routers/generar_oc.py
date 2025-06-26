from fastapi import APIRouter, HTTPException
from app.adapters.outbound.database.models.cotizacion_model import CotizacionModel
from app.adapters.outbound.database.models.proveedor_contacto_model import ContactoProveedorModel

# Configuración de la API
router = APIRouter(
    prefix="/generar-oc", 
    tags=["Generar OC"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", summary="Ingrese el id de la cotizacion")
async def upload_xml(id_cotizacion: int, id_version: int, id_contacto_proveedor: int):  
    cotizacion = CotizacionModel.get_cotizacion(id_cotizacion)
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotizacion no encontrada")
    
    version = cotizacion.get_version(id_version)
    if not version:
        raise HTTPException(status_code=404, detail="Version no encontrada")
    
    contacto_proveedor = ContactoProveedorModel.get_contacto_proveedor(id_contacto_proveedor)
    if not contacto_proveedor:
        raise HTTPException(status_code=404, detail="Contacto proveedor no encontrado")
    
    
    
    
    

    return {"message": "OC generada correctamente"}






