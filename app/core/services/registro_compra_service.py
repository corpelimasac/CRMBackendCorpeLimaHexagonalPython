"""
Servicio de cálculo de montos consolidados para registro de compras
"""
from typing import List
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from app.adapters.outbound.database.models.ordenes_compra_model import OrdenesCompraModel
import logging

logger = logging.getLogger(__name__)


class RegistroCompraService:
    """
    Servicio que contiene la lógica de cálculo de montos consolidados
    """

    IGV_PERCENTAGE = Decimal('1.18')  # 18%

    def calcular_montos_consolidados(
        self,
        ordenes: List[OrdenesCompraModel],
        tipo_cambio_sunat: Decimal = None
    ) -> dict:
        """
        Calcula montos consolidados para un conjunto de órdenes de compra

        Lógica:
        1. Si hay mezcla de monedas (PEN y USD):
           - Convertir PEN a USD
           - Sumar todo en USD
           - Convertir total USD a PEN
        2. Si solo hay una moneda:
           - USD → Convertir a PEN
           - PEN → Usar directo
        3. Calcular monto sin IGV (dividir entre 1.18)

        Args:
            ordenes: Lista de órdenes de compra de la misma cotización
            tipo_cambio_sunat: Tipo de cambio SUNAT (venta). Si None, se debe proporcionar

        Returns:
            dict: {
                'moneda': str,
                'monto_total_dolar': Decimal,
                'tipo_cambio_sunat': Decimal,
                'monto_total_soles': Decimal,
                'monto_sin_igv': Decimal,
                'fecha_orden_compra': date,
                'tipo_empresa': str
            }

        Raises:
            ValueError: Si tipo_cambio_sunat es None o no hay órdenes
        """
        if not ordenes:
            raise ValueError("No hay órdenes para calcular")

        if tipo_cambio_sunat is None:
            raise ValueError("Tipo de cambio SUNAT es requerido")

        logger.info(f"Calculando montos para {len(ordenes)} órdenes con TC={tipo_cambio_sunat}")

        # Separar órdenes por moneda (normalizar nombres: DOLARES/USD y SOLES/PEN)
        ordenes_pen = [o for o in ordenes if o.moneda and o.moneda.upper() in ('PEN', 'SOLES')]
        ordenes_usd = [o for o in ordenes if o.moneda and o.moneda.upper() in ('USD', 'DOLARES')]

        logger.info(f"Órdenes en PEN: {len(ordenes_pen)}, Órdenes en USD: {len(ordenes_usd)}")

        # Calcular total en cada moneda
        total_pen = sum(
            Decimal(str(o.total)) for o in ordenes_pen if o.total
        )
        total_usd = sum(
            Decimal(str(o.total)) for o in ordenes_usd if o.total
        )

        logger.info(f"Total PEN: {total_pen}, Total USD: {total_usd}")

        # Convertir PEN a USD
        total_usd_convertido = Decimal('0')
        if total_pen > 0:
            total_usd_convertido = total_pen / tipo_cambio_sunat
            logger.info(f"PEN convertido a USD: {total_usd_convertido}")

        # Sumar todo en USD
        monto_total_dolar = total_usd + total_usd_convertido

        # Convertir total USD a PEN
        monto_total_soles = monto_total_dolar * tipo_cambio_sunat

        # Quitar IGV (18%) - dividir entre 1.18
        monto_sin_igv = monto_total_soles / self.IGV_PERCENTAGE

        # Redondear a 2 decimales
        monto_total_dolar = monto_total_dolar.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        monto_total_soles = monto_total_soles.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        monto_sin_igv = monto_sin_igv.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Determinar tipo de moneda para identificar el origen de las órdenes
        # MIX = órdenes mixtas (PEN + USD), USD = solo USD, PEN = solo PEN
        # Aunque el resultado final siempre está en PEN, este campo indica el origen
        if len(ordenes_pen) > 0 and len(ordenes_usd) > 0:
            moneda = 'MIX'  # Mixto: órdenes en PEN y USD
        elif len(ordenes_usd) > 0:
            moneda = 'USD'  # Solo órdenes en USD
        elif len(ordenes_pen) > 0:
            moneda = 'PEN'  # Solo órdenes en PEN
        else:
            # Fallback: si no se puede determinar, usar PEN por defecto
            moneda = 'PEN'

        # Determinar tipo de empresa basado en el campo 'consorcio' de las órdenes
        # Si al menos una orden es de consorcio, todo el registro es CONSORCIO
        tiene_consorcio = any(orden.consorcio for orden in ordenes)
        tipo_empresa = 'CONSORCIO' if tiene_consorcio else 'CORPELIMA'
        
        logger.info(f"Tipo de empresa determinado: {tipo_empresa} (consorcio={tiene_consorcio})")

        # Fecha del registro (fecha actual cuando se genera el registro)
        fecha_orden_compra = date.today()

        resultado = {
            'moneda': moneda,
            'monto_total_dolar': monto_total_dolar,
            'tipo_cambio_sunat': tipo_cambio_sunat,
            'monto_total_soles': monto_total_soles,
            'monto_sin_igv': monto_sin_igv,
            'fecha_orden_compra': fecha_orden_compra,
            'tipo_empresa': tipo_empresa
        }

        logger.info(f"✅ Cálculo completado: Moneda={moneda}, Soles={monto_total_soles}, Sin IGV={monto_sin_igv}")

        return resultado
