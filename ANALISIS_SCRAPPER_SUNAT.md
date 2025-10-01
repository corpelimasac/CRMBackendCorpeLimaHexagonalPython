# Análisis del Endpoint `/obtener-ruc/{ruc}` y Estrategias de Optimización

## 1. ¿Qué es el WebDriver?

**WebDriver** es una interfaz de automatización de navegadores web que forma parte del proyecto Selenium. Permite controlar navegadores web de forma programática como si fuera un usuario real.

### Características principales:

- **Automatización de navegadores**: Controla Chrome, Firefox, Safari, etc. programáticamente
- **Interacción con páginas web**: Puede hacer clic, rellenar formularios, navegar entre páginas
- **Extracción de datos**: Accede al DOM (Document Object Model) para extraer información
- **Ejecución de JavaScript**: Puede ejecutar scripts dentro del navegador

### En tu código:

El proyecto utiliza **Selenium WebDriver con Chrome** en modo headless (sin interfaz gráfica) para realizar web scraping en el sitio de SUNAT:

```python
# Ubicación: app/adapters/outbound/external_services/sunat/sunat_scraper.py:68-106

def _create_driver(self):
    """Crea una nueva instancia de WebDriver"""
    options = self._get_chrome_options()

    # Configuración headless para servidor
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Crea instancia de Chrome automatizado
    driver = webdriver.Chrome(service=service, options=options)
    return driver
```

### ¿Cómo funciona el scraper?

1. **WebDriverManager Singleton**: Mantiene una única instancia del navegador Chrome activa por 12 horas
2. **Navegación automatizada**: Accede a la página de SUNAT (`https://e-consultaruc.sunat.gob.pe/...`)
3. **Interacción**: Rellena el formulario con el RUC y hace clic en "Consultar"
4. **Extracción de datos**: Lee el DOM para obtener información del contribuyente
5. **Navegación adicional**: Hace clics en botones para ver información de trabajadores y representantes legales
6. **Reintentos**: Implementa lógica de 3 intentos con manejo de timeouts

---

## 2. Problema de Rendimiento y Estrategias de Optimización

### Diagnóstico del Problema Actual

El endpoint es **extremadamente lento** por las siguientes razones:

#### A. Naturaleza del WebDriver (10-30 segundos por consulta)
- Lanza un navegador Chrome completo (aunque sea headless)
- Carga HTML, CSS, JavaScript completo de SUNAT
- Espera a que elementos DOM estén disponibles con `WebDriverWait`
- Realiza múltiples navegaciones (página principal → trabajadores → representantes)

#### B. Limitaciones de Railway
- **Recursos limitados**: CPU y memoria restringidas en planes gratuitos/básicos
- **Latencia de red**: El servidor debe conectarse a SUNAT desde su ubicación
- **Cold starts**: Si el contenedor se suspende, el primer request es muy lento
- **ChromeDriver pesado**: Chrome consume mucha memoria (~200-300MB por instancia)

#### C. Arquitectura actual
- **Singleton de 12 horas**: Aunque reutiliza el driver, sigue siendo lento por navegación
- **Operaciones síncronas**: Aunque usa `modo_rapido`, aún necesita cargar páginas completas
- **Sin caché**: Cada consulta golpea SUNAT directamente

---

## 3. Estrategias de Optimización

### 🔥 Estrategia 1: Implementar Sistema de Caché (IMPACTO ALTO - PRIORIDAD 1)

**Beneficio**: Reduce el 80-90% de consultas reales a SUNAT

#### Opción A: Caché en Memoria con TTL (Rápida implementación)

```python
# Implementar con Redis o caché en memoria
from cachetools import TTLCache
from datetime import timedelta

cache_ruc = TTLCache(maxsize=1000, ttl=86400)  # 24 horas

async def obtener_ruc(self, ruc: str) -> Dict:
    # Verificar caché primero
    if ruc in cache_ruc:
        print(f"✅ RUC {ruc} encontrado en caché")
        return cache_ruc[ruc]

    # Si no está en caché, hacer scraping
    resultado = self.sunat_scraper.consultar_ruc(ruc)
    cache_ruc[ruc] = resultado
    return resultado
```

**Ventajas**:
- Respuesta instantánea para RUCs consultados recientemente
- Reduce carga en Railway y SUNAT
- Fácil de implementar

**Desventajas**:
- Datos pueden quedar desactualizados (configurar TTL apropiado)
- Se pierde al reiniciar el servidor

#### Opción B: Caché Persistente con Redis (Recomendado)

```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

async def obtener_ruc(self, ruc: str) -> Dict:
    # Buscar en Redis
    cached = redis_client.get(f"ruc:{ruc}")
    if cached:
        return json.loads(cached)

    # Hacer scraping
    resultado = self.sunat_scraper.consultar_ruc(ruc)

    # Guardar en Redis con expiración de 7 días
    redis_client.setex(
        f"ruc:{ruc}",
        timedelta(days=7),
        json.dumps(resultado)
    )
    return resultado
```

**Ventajas**:
- Persistencia entre reinicios
- Railway ofrece Redis como add-on
- Puede compartirse entre múltiples instancias

#### Opción C: Base de Datos PostgreSQL (Más robusto)

```python
# Guardar resultados en BD con timestamp
async def obtener_ruc(self, ruc: str) -> Dict:
    # Buscar en BD (últimos 7 días)
    cached = await db.query(
        "SELECT * FROM ruc_cache WHERE ruc = $1 AND updated_at > NOW() - INTERVAL '7 days'",
        ruc
    )
    if cached:
        return cached

    # Hacer scraping y guardar
    resultado = self.sunat_scraper.consultar_ruc(ruc)
    await db.execute(
        "INSERT INTO ruc_cache (ruc, data, updated_at) VALUES ($1, $2, NOW()) "
        "ON CONFLICT (ruc) DO UPDATE SET data = $2, updated_at = NOW()",
        ruc, json.dumps(resultado)
    )
    return resultado
```

**Ventajas**:
- Datos persistentes e históricos
- Permite analytics y auditoría
- Mayor control sobre invalidación

---

### ⚡ Estrategia 2: Cambiar de Selenium a Requests + BeautifulSoup (IMPACTO MEDIO-ALTO)

**Beneficio**: 5-10x más rápido, consume 90% menos recursos

El sitio de SUNAT no requiere JavaScript para consultas básicas, por lo que puedes usar HTTP directo:

```python
import requests
from bs4 import BeautifulSoup

def consultar_ruc_rapido(ruc: str) -> Dict:
    # Hacer request HTTP directo
    url = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias"

    payload = {
        'accion': 'consPorRuc',
        'nroRuc': ruc
    }

    response = requests.post(url, data=payload, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extraer datos del HTML
    razon_social = soup.find('h4', string=lambda t: 'Número de RUC:' in t)
    # ... resto de extracción

    return datos
```

**Ventajas**:
- **10-100x más rápido** que Selenium
- Consume solo ~10-20MB de RAM vs 200-300MB de Chrome
- Más estable y menos propenso a errores
- Railway puede manejar muchas más solicitudes concurrentes

**Desventajas**:
- Requiere reescribir la lógica de extracción
- Si SUNAT cambia la estructura HTML, hay que actualizar
- Puede requerir manejar headers/cookies para evitar bloqueos

**Recomendación**: Este cambio tiene el **mayor impacto** en rendimiento. Combínalo con caché para resultados óptimos.

---

### 🚀 Estrategia 3: Implementar Queue + Worker Background (IMPACTO MEDIO)

Si las consultas deben ser síncronas pero puedes tolerar cierta latencia, usa un sistema de colas:

```python
# FastAPI endpoint
@router.get("/obtener-ruc/{ruc}")
async def obtener_ruc(ruc: str):
    # Verificar caché
    cached = await cache.get(ruc)
    if cached:
        return cached

    # Agregar a cola de procesamiento
    job_id = await queue.enqueue('scrape_ruc', ruc)

    return {
        "status": "processing",
        "job_id": job_id,
        "check_url": f"/obtener-ruc/status/{job_id}"
    }

# Worker en background procesa la cola
# El cliente hace polling al endpoint de status
```

**Ventajas**:
- API responde inmediatamente
- Workers pueden escalar independientemente
- Evita timeouts de Railway

**Desventajas**:
- Requiere cambios en el frontend
- Más complejidad arquitectónica

---

### 🔧 Estrategia 4: Optimizaciones de Railway y Deployment

#### A. Aumentar recursos del plan
- **Railway Pro**: Más CPU/RAM para manejar Chrome
- **Dedicated instances**: Evita cold starts

#### B. Configurar timeout apropiados
```python
# Aumentar timeouts en Railway
# railway.json
{
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

#### C. Pre-calentar el WebDriver
```python
# Al iniciar la app, crear el driver inmediatamente
@app.on_event("startup")
async def startup_event():
    scraper = SunatScraper()
    scraper.get_driver()  # Inicializa Chrome
    print("✅ WebDriver pre-calentado")
```

#### D. Usar imagen Docker optimizada
```dockerfile
# Usar imagen más ligera con Chrome pre-instalado
FROM zenika/alpine-chrome:latest
# O usar Playwright que es más eficiente que Selenium
```

---

### 📊 Estrategia 5: API Oficial de SUNAT (IMPACTO ALTO - Largo Plazo)

SUNAT ofrece APIs oficiales para consultas:

- **API REST de SUNAT**: Requiere registro y autenticación
- **Web Service SOAP**: Más complejo pero oficial
- **Servicio de Padrones**: Para consultas masivas

**Ventajas**:
- Datos oficiales y actualizados
- Sin riesgo de bloqueo
- Mucho más rápido y estable

**Desventajas**:
- Requiere trámites y permisos
- Posiblemente tenga costos
- Tiempo de implementación

---

## 4. Plan de Acción Recomendado (Priorizado)

### Fase 1: Quick Wins (1-3 días) 🎯
1. **Implementar caché con Redis** (o TTLCache si Redis no está disponible)
   - TTL: 7 días para datos básicos
   - TTL: 1 día para trabajadores/representantes
   - Reducción esperada: **80-90% de consultas a SUNAT**

2. **Pre-calentar WebDriver al startup**
   - Elimina cold start del primer request

3. **Ajustar timeouts y reintentos**
   - Reducir de 3 a 2 reintentos
   - Timeouts más agresivos en Railway

### Fase 2: Optimización Media (1 semana) ⚡
4. **Migrar de Selenium a Requests + BeautifulSoup**
   - Reescribir `sunat_scraper.py` con requests
   - Testing exhaustivo
   - **Impacto esperado: 5-10x más rápido**

5. **Implementar monitoreo**
   - Logs de tiempo de respuesta
   - Métricas de cache hit rate
   - Alertas de timeouts

### Fase 3: Arquitectura Robusta (2-3 semanas) 🏗️
6. **Implementar sistema de colas (opcional)**
   - Celery + Redis o Bull Queue
   - Worker separado para scraping
   - API asíncrona con webhooks

7. **Evaluar Railway Pro**
   - Más recursos si el volumen justifica
   - O considerar alternativas (Render, Fly.io)

### Fase 4: Solución Definitiva (Largo plazo) 🎓
8. **Migrar a API oficial de SUNAT**
   - Investigar requisitos
   - Realizar trámites necesarios
   - Implementación gradual

---

## 5. Estimación de Mejoras

| Estrategia | Tiempo de Implementación | Reducción de Latencia | Dificultad |
|-----------|-------------------------|----------------------|-----------|
| Caché Redis | 1-2 días | 90% (para hits) | Baja |
| Requests vs Selenium | 3-5 días | 80-90% | Media |
| Queue + Workers | 1-2 semanas | 50% (percibida) | Media-Alta |
| API Oficial SUNAT | 1-2 meses | 95% | Alta |
| Railway Pro | Inmediato | 30-50% | Baja |

---

## 6. Código de Ejemplo: Caché con Redis

```python
# app/core/use_cases/integracion_sunat/integracion_sunat_uc.py
import redis
import json
from datetime import timedelta

class IntegracionSunatUC:
    def __init__(self, sunat_scraper: SunatScraper):
        self.sunat_scraper = sunat_scraper
        # Conectar a Redis (Railway lo proporciona como add-on)
        self.redis_client = redis.from_url(
            os.getenv('REDIS_URL', 'redis://localhost:6379'),
            decode_responses=True
        )
        self.cache_ttl = 604800  # 7 días en segundos

    async def obtener_ruc(self, ruc: str, max_intentos: int = 3) -> Dict:
        # Validar formato
        if not self._validar_ruc(ruc):
            return {...}

        # 1. BUSCAR EN CACHÉ PRIMERO
        try:
            cache_key = f"sunat:ruc:{ruc}"
            cached_data = self.redis_client.get(cache_key)

            if cached_data:
                print(f"✅ Cache HIT para RUC {ruc}")
                return json.loads(cached_data)
            else:
                print(f"❌ Cache MISS para RUC {ruc}")
        except Exception as e:
            print(f"⚠️ Error accediendo a caché: {e}")

        # 2. SI NO ESTÁ EN CACHÉ, HACER SCRAPING
        ultimo_error = None
        for intento in range(1, max_intentos + 1):
            try:
                resultado = self.sunat_scraper.consultar_ruc(ruc, modo_rapido=True)

                # Verificar si hubo error
                if "error" in resultado:
                    # ... manejo de errores
                    continue

                # 3. GUARDAR EN CACHÉ SI LA CONSULTA FUE EXITOSA
                try:
                    self.redis_client.setex(
                        cache_key,
                        self.cache_ttl,
                        json.dumps(resultado)
                    )
                    print(f"💾 RUC {ruc} guardado en caché por {self.cache_ttl} segundos")
                except Exception as e:
                    print(f"⚠️ Error guardando en caché: {e}")

                return resultado

            except Exception as e:
                # ... manejo de errores
                pass

        return {...}  # Error
```

---

## 7. Conclusiones

### Problema principal
El scraping con Selenium WebDriver es **inherentemente lento** (10-30 segundos por consulta) y consume muchos recursos en Railway.

### Solución recomendada (combinación)
1. **Caché agresivo** con Redis → Elimina 80-90% de consultas lentas
2. **Migrar a requests/BeautifulSoup** → 5-10x más rápido que Selenium
3. **Optimizar Railway** → Más recursos o configuración mejorada

### Resultado esperado
- **Tiempo con caché (hit)**: < 100ms (reducción del 99%)
- **Tiempo sin caché (miss)**: 2-5 segundos con requests (vs 10-30s actual)
- **Capacidad**: 10-20x más solicitudes concurrentes

### Próximos pasos
1. Implementar Redis en Railway
2. Añadir capa de caché al use case
3. Evaluar migración a requests
4. Monitorear métricas de rendimiento
