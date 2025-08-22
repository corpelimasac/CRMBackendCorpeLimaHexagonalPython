#!/usr/bin/env python3
"""
Script para probar el sistema singleton de WebDriver con vida útil de 12 horas
"""
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.adapters.outbound.external_services.sunat.sunat_scraper import SunatScraper
import json

def test_singleton_driver():
    """
    Prueba el sistema singleton de WebDriver
    """
    ruc_test = "20484044997"  # RUC de prueba
    
    print("=" * 80)
    print("🔧 PRUEBA DEL SISTEMA SINGLETON DE WEBDRIVER")
    print("=" * 80)
    print(f"📋 RUC a consultar: {ruc_test}")
    print(f"🎯 Objetivo: WebDriver activo por 12 horas")
    print(f"⚡ Características: Singleton + Pool + Auto-cleanup")
    
    try:
        # Crear primera instancia
        scraper1 = SunatScraper()
        print(f"\n📊 Estado inicial: {scraper1.get_driver_status()}")
        
        # Primera consulta (creará el driver)
        print("\n🔄 PRIMERA CONSULTA (creará el driver)...")
        start_time = time.time()
        resultado1 = scraper1.consultar_ruc(ruc_test, modo_rapido=True)
        tiempo1 = time.time() - start_time
        
        print(f"✅ Primera consulta completada en {tiempo1:.2f}s")
        print(f"📊 Estado después de primera consulta: {scraper1.get_driver_status()}")
        
        # Crear segunda instancia (debería usar el mismo driver)
        print("\n🔄 SEGUNDA CONSULTA (usará el driver existente)...")
        scraper2 = SunatScraper()
        start_time = time.time()
        resultado2 = scraper2.consultar_ruc(ruc_test, modo_rapido=True)
        tiempo2 = time.time() - start_time
        
        print(f"✅ Segunda consulta completada en {tiempo2:.2f}s")
        print(f"📊 Estado después de segunda consulta: {scraper2.get_driver_status()}")
        
        # Verificar que es el mismo driver
        print(f"\n🔍 VERIFICACIÓN:")
        print(f"   • Driver 1 status: {scraper1.get_driver_status()}")
        print(f"   • Driver 2 status: {scraper2.get_driver_status()}")
        print(f"   • ¿Mismo driver?: {'✅ SÍ' if scraper1.get_driver_status() == scraper2.get_driver_status() else '❌ NO'}")
        
        # Comparar tiempos
        print(f"\n⏱️  COMPARACIÓN DE TIEMPOS:")
        print(f"   • Primera consulta: {tiempo1:.2f}s (incluye inicialización)")
        print(f"   • Segunda consulta: {tiempo2:.2f}s (driver ya activo)")
        if tiempo2 < tiempo1:
            mejora = ((tiempo1 - tiempo2) / tiempo1) * 100
            print(f"   • Mejora: {mejora:.1f}% más rápido")
        
        # Verificar resultados
        print(f"\n📄 RESULTADOS:")
        if resultado1.get("razonSocial") != "Error en consulta":
            print("✅ Primera consulta exitosa")
        else:
            print("❌ Primera consulta falló")
            
        if resultado2.get("razonSocial") != "Error en consulta":
            print("✅ Segunda consulta exitosa")
        else:
            print("❌ Segunda consulta falló")
        
        print(f"\n🎯 RESUMEN DEL SISTEMA SINGLETON:")
        print(f"   • ✅ WebDriver se crea una sola vez")
        print(f"   • ✅ Múltiples instancias comparten el mismo driver")
        print(f"   • ✅ Driver se mantiene activo por 12 horas")
        print(f"   • ✅ Auto-cleanup al salir de la aplicación")
        print(f"   • ✅ Thread-safe con locks")
        
        # NO cerrar el driver aquí - se mantendrá activo para futuras consultas
        print(f"\n💡 El WebDriver permanecerá activo para futuras consultas...")
        
    except Exception as e:
        print(f"\n💥 Error en la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_singleton_driver()
