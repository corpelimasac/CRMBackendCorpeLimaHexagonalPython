#!/usr/bin/env python3
"""
Script de prueba para el generador de Excel
"""
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.shared.serializers.generator_oc.generador import Generador

def test_generador():
    """Prueba básica del generador"""
    
    # Datos de prueba
    datos_prueba = [
        {
            'CANT': 5,
            'UMED': 'UNIDADES',
            'PRODUCTO': 'Laptop Dell Inspiron',
            'MARCA': 'Dell',
            'MODELO': 'Inspiron 15',
            'P.UNIT': 2500.00,
            'PROVEEDOR': 'Tecnología ABC S.A.',
            'PERSONAL': 'Juan Pérez',
            'CELULAR': '999888777',
            'CORREO': 'juan.perez@abc.com',
            'DIRECCION': 'Av. Principal 123, Lima',
            'FECHA': '2024-01-15',
            'MONEDA': 'SOLES',
            'PAGO': '30 días'
        },
        {
            'CANT': 3,
            'UMED': 'UNIDADES',
            'PRODUCTO': 'Mouse Inalámbrico',
            'MARCA': 'Logitech',
            'MODELO': 'M185',
            'P.UNIT': 45.00,
            'PROVEEDOR': 'Tecnología ABC S.A.',
            'PERSONAL': 'Juan Pérez',
            'CELULAR': '999888777',
            'CORREO': 'juan.perez@abc.com',
            'DIRECCION': 'Av. Principal 123, Lima',
            'FECHA': '2024-01-15',
            'MONEDA': 'SOLES',
            'PAGO': '30 días'
        }
    ]
    
    try:
        print("Iniciando prueba del generador...")
        
        # Crear instancia del generador
        generador = Generador(
            num_orden="OC-00001",
            oc=datos_prueba,
            proveedor="Tecnología ABC S.A.",
            igv=1
        )
        
        print("Generador creado exitosamente")
        print(f"Directorio de salida: {generador.output_folder}")
        print(f"Archivo de salida: {generador.output_file}")
        
        # Generar el Excel
        generador.generar_excel()
        
        print("¡Prueba completada exitosamente!")
        
    except Exception as e:
        print(f"Error en la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_generador() 