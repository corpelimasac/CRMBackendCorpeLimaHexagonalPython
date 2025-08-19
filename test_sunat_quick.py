"""
Prueba rápida del servicio de SUNAT optimizado
"""
import asyncio
import time
from app.core.use_cases.integracion_sunat.integracion_sunat_uc import IntegracionSunatUC
from app.adapters.outbound.external_services.sunat.sunat_scraper import SunatScraper


async def test_ruc_optimizado():
    """
    Prueba rápida con el RUC que estaba fallando
    """
    ruc_test = "20512081372"  # El RUC que estaba dando problemas
    
    print(f"🚀 Probando RUC optimizado: {ruc_test}")
    print(f"⏰ Iniciando a las: {time.strftime('%H:%M:%S')}")
    
    start_time = time.time()
    
    # Crear instancias
    sunat_scraper = SunatScraper()
    use_case = IntegracionSunatUC(sunat_scraper)
    
    try:
        # Realizar consulta con reintentos
        resultado = await use_case.obtener_ruc(ruc_test, max_intentos=2)
        
        end_time = time.time()
        duracion = end_time - start_time
        
        print(f"⏱️  Tiempo total: {duracion:.2f} segundos")
        
        if "message" in resultado and "error" in resultado.get("detail", "").lower():
            print("❌ Error en la consulta:")
            print(f"   Mensaje: {resultado['message']}")
            print(f"   Detalle: {resultado['detail']}")
        else:
            print("✅ Consulta exitosa!")
            print(f"📄 RUC: {resultado.get('numeroDocumento', 'N/A')}")
            print(f"🏢 Razón Social: {resultado.get('razonSocial', 'N/A')}")
            print(f"📍 Distrito: {resultado.get('distrito', 'N/A')}")
            print(f"👥 Trabajadores: {resultado.get('numeroTrabajadores', 'N/A')}")
            print(f"👤 Rep. Legal: {resultado.get('representanteLegal', {}).get('nombre', 'N/A')}")
        
    except Exception as e:
        end_time = time.time()
        duracion = end_time - start_time
        print(f"❌ Error después de {duracion:.2f} segundos: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"🏁 Finalizando a las: {time.strftime('%H:%M:%S')}")


if __name__ == "__main__":
    asyncio.run(test_ruc_optimizado())
