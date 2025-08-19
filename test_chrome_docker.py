"""
Script para probar Chrome en contenedor Docker
"""
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService


def test_chrome_installation():
    """
    Verifica que Chrome y ChromeDriver estén instalados correctamente
    """
    print("🔍 Verificando instalación de Chrome...")
    
    # Verificar si Chrome está instalado
    chrome_paths = [
        '/usr/bin/google-chrome',
        '/usr/bin/google-chrome-stable',
        '/usr/bin/chromium-browser'
    ]
    
    chrome_found = False
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✅ Chrome encontrado en: {path}")
            chrome_found = True
            break
    
    if not chrome_found:
        print("❌ Chrome no encontrado")
        return False
    
    # Verificar ChromeDriver
    chromedriver_paths = [
        '/usr/bin/chromedriver',
        '/opt/chromedriver/chromedriver'
    ]
    
    chromedriver_found = False
    for path in chromedriver_paths:
        if os.path.exists(path):
            print(f"✅ ChromeDriver encontrado en: {path}")
            chromedriver_found = True
            break
    
    if not chromedriver_found:
        print("❌ ChromeDriver no encontrado")
        return False
    
    return True


def test_chrome_functionality():
    """
    Prueba básica de funcionalidad de Chrome
    """
    print("\n🚀 Probando funcionalidad de Chrome...")
    
    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    driver = None
    try:
        # Usar ChromeDriver del sistema
        if os.path.exists('/usr/bin/chromedriver'):
            service = ChromeService(executable_path='/usr/bin/chromedriver')
        else:
            from webdriver_manager.chrome import ChromeDriverManager
            service = ChromeService(executable_path=ChromeDriverManager().install())
        
        driver = webdriver.Chrome(service=service, options=options)
        
        # Probar navegación básica
        print("📄 Navegando a Google...")
        driver.get("https://www.google.com")
        
        title = driver.title
        print(f"✅ Título de la página: {title}")
        
        if "Google" in title:
            print("✅ Navegación exitosa")
            return True
        else:
            print("❌ Título inesperado")
            return False
            
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return False
    finally:
        if driver:
            driver.quit()


def test_sunat_connectivity():
    """
    Prueba conectividad con SUNAT
    """
    print("\n🌐 Probando conectividad con SUNAT...")
    
    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    driver = None
    try:
        if os.path.exists('/usr/bin/chromedriver'):
            service = ChromeService(executable_path='/usr/bin/chromedriver')
        else:
            from webdriver_manager.chrome import ChromeDriverManager
            service = ChromeService(executable_path=ChromeDriverManager().install())
        
        driver = webdriver.Chrome(service=service, options=options)
        
        # Probar acceso a SUNAT
        sunat_url = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/FrameCriterioBusquedaWeb.jsp"
        print(f"📄 Navegando a: {sunat_url}")
        
        driver.set_page_load_timeout(30)
        driver.get(sunat_url)
        
        title = driver.title
        print(f"✅ Título de SUNAT: {title}")
        
        # Verificar que el campo de RUC existe
        ruc_field = driver.find_element("id", "txtRuc")
        if ruc_field:
            print("✅ Campo de RUC encontrado")
            return True
        else:
            print("❌ Campo de RUC no encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando con SUNAT: {e}")
        return False
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    print("🐳 Pruebas de Chrome en Docker\n")
    
    # Ejecutar pruebas
    installation_ok = test_chrome_installation()
    
    if installation_ok:
        functionality_ok = test_chrome_functionality()
        
        if functionality_ok:
            sunat_ok = test_sunat_connectivity()
            
            if sunat_ok:
                print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
                exit(0)
    
    print("\n💥 Algunas pruebas fallaron")
    exit(1)
