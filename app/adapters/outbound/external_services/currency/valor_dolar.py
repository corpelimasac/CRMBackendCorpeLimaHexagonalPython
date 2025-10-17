import requests
from bs4 import BeautifulSoup
from datetime import datetime

class ValorDolar:
    def __init__(self):
        self.url = 'https://securex.pe/'
        self.session = requests.Session()  # Reutilizar la sesión para eficiencia

    def obtener_cambio(self):
        """Obtener los valores de compra y venta del dólar"""
        try:
            response = self.session.get(self.url, timeout=10)
            response.raise_for_status()  # Levantar error si el estado no es 200
        except requests.RequestException as e:
            print(f"Error en la solicitud HTTP: {e}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        try:
            compra_value = float(soup.find('div', id='item_compra').find_all('span')[1].text.strip())
            venta_value = float(soup.find('div', id='item_venta').find_all('span')[1].text.strip())
            print("Valores obtenidos:", compra_value, venta_value)
        except (AttributeError, ValueError) as e:
            print(f"Error al extraer datos del HTML: {e}")
            return None

        return {
            "compra": compra_value,
            "venta": venta_value,
            "fecha": datetime.now().strftime("%d-%m-%Y %H:%M")
        } 