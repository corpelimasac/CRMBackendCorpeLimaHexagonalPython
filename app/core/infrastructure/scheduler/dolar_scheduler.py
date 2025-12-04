import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from app.config.database import SessionLocal
from app.adapters.outbound.external_services.currency.valor_dolar import ValorDolar
from app.adapters.outbound.database.repositories.valor_dolar_repository import ValorDolarRepository

logger = logging.getLogger(__name__)


class DolarSchedulerService:
    """
    Servicio para programar la actualización automática del valor del dólar.

    Este servicio ejecuta un scraping del sitio web de Securex para obtener
    el valor del dólar y lo guarda en la base de datos automáticamente
    todos los días a las 10:00 AM hora Perú (America/Lima).
    """

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scraper = ValorDolar()
        # Configurar timezone de Perú
        self.peru_tz = timezone('America/Lima')

    def actualizar_valor_dolar(self):
        """
        Función que ejecuta el scraping y guarda el valor del dólar en la BD.
        Esta es la tarea que se ejecutará de forma programada.
        """
        db = SessionLocal()
        try:
            logger.info("=" * 80)
            logger.info("🚀 INICIO - Actualización programada del valor del dólar")
            print("=" * 80)
            print("🚀 INICIO - Actualización programada del valor del dólar")

            # Obtener el valor del dólar mediante scraping
            data = self.scraper.obtener_cambio()

            if not data:
                logger.error("❌ No se pudo obtener el valor del dólar desde Securex")
                print("❌ No se pudo obtener el valor del dólar desde Securex")
                return

            logger.info(f"📊 Valores obtenidos - Compra: {data['compra']}, Venta: {data['venta']}")
            print(f"📊 Valores obtenidos - Compra: {data['compra']}, Venta: {data['venta']}")

            # Crear repositorio y guardar en BD
            repo = ValorDolarRepository(db)

            # Aumentar el valor de la venta en 0.03 (según lógica del endpoint)
            logger.info("📈 Aumentando el valor de la venta en 0.03")
            print("📈 Aumentando el valor de la venta en 0.03")
            data["venta"] = data["venta"] + 0.03

            # Guardar en base de datos
            repo.create_valor_dolar(data)

            logger.info(f"✅ Valor del dólar actualizado exitosamente - Venta final: {data['venta']}, Compra: {data['compra']}")
            logger.info("=" * 80)
            print(f"✅ Valor del dólar actualizado exitosamente - Venta final: {data['venta']}, Compra: {data['compra']}")
            print("=" * 80)

        except Exception as e:
            logger.error(f"❌ Error al actualizar el valor del dólar: {e}", exc_info=True)
            print(f"❌ Error al actualizar el valor del dólar: {e}")

        finally:
            db.close()

    def start(self):
        """
        Inicia el scheduler con la tarea programada.
        Configura la ejecución diaria a las 10:00 AM hora Perú.
        """
        try:
            # Programar la tarea para ejecutarse todos los días a las 10:00 AM hora Perú
            self.scheduler.add_job(
                func=self.actualizar_valor_dolar,
                trigger=CronTrigger(hour=8, minute=30, timezone=self.peru_tz),
                id='actualizar_dolar_diario',
                name='Actualización diaria del valor del dólar',
                replace_existing=True
            )

            # Iniciar el scheduler
            self.scheduler.start()

            logger.info("✅ Scheduler del dólar iniciado correctamente")
            logger.info("📅 Programado para ejecutarse todos los días a las 10:00 AM (hora Perú)")
            print("✅ Scheduler del dólar iniciado correctamente")
            print("📅 Programado para ejecutarse todos los días a las 10:00 AM (hora Perú)")

        except Exception as e:
            logger.error(f"❌ Error al iniciar el scheduler: {e}", exc_info=True)
            print(f"❌ Error al iniciar el scheduler: {e}")

    def shutdown(self):
        """
        Detiene el scheduler de forma segura.
        """
        try:
            self.scheduler.shutdown()
            logger.info("🛑 Scheduler del dólar detenido")
            print("🛑 Scheduler del dólar detenido")
        except Exception as e:
            logger.error(f"❌ Error al detener el scheduler: {e}", exc_info=True)
            print(f"❌ Error al detener el scheduler: {e}")


# Instancia global del scheduler
dolar_scheduler = DolarSchedulerService()
