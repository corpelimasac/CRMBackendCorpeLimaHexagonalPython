from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.adapters.outbound.external_services.currency.valor_dolar import ValorDolar
from app.adapters.outbound.database.repositories.valor_dolar_repository import ValorDolarRepository

# Configuración de la API
router = APIRouter(
    prefix="/dolar", 
    tags=["Dolar"],
)
scraper = ValorDolar()

@router.get("/ultimo")
async def get_dolar_ultimo(db: Session = Depends(get_db)):
    repo = ValorDolarRepository(db)
    consulta = repo.fetch_last_value_dolar()
    if consulta:
        return {"fecha": consulta.fecha, "venta": consulta.venta}, 200
    else:
        return {"error": "No hay datos en la base de datos."}, 404  

@router.post("/guardarNuevoValor")
async def guardar_nuevo_valor(db: Session = Depends(get_db)):
    repo = ValorDolarRepository(db)
    
    data = scraper.obtener_cambio()
    if not data:
        return {"error": "No se pudo obtener el valor del dólar."}, 500
    
    consulta = repo.fetch_last_value_dolar()
    print("Aumentar el valor de la venta en 0.03")
    data["venta"] = data["venta"] + 0.03
    if consulta:
        repo.create_valor_dolar(data)
        return {"mensaje": "Precio del dolar actualizado.",
                "venta":data["venta"],
                "compra":data["compra"]}, 200
    else:
        return {"mensaje": "ERROR: No se pudo obtener el valor del dólar."}, 500
    ##if consulta:
    ##    venta_consulta = consulta.venta
     ##   if abs(data["venta"] - venta_consulta) >= 0.03:
     #3       repo.create_valor_dolar(data)
     #       return {"mensaje": "Datos actualizados en la base de datos.", "data": data}, 201
     #   else:
     #       return {"mensaje": "Dólar vigente, no es necesario actualizar.",
     #           "venta":data["venta"],
     #           "compra":data["compra"]}, 200
    #else:
    #    repo.create_valor_dolar(data)
    #    return {"mensaje": "Primer registro insertado.", "data": data}, 201



