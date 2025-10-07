# Sistema de Eventos para Registro de Compras

## 📋 Descripción

Sistema de eventos transaccionales asíncronos que procesa automáticamente el cálculo y registro de compras cada vez que se crea o edita una Orden de Compra (OC).

Implementa el patrón equivalente a Spring Boot:
```java
@Async("calculoFinancieroExecutor")
@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
@Transactional(propagation = Propagation.REQUIRES_NEW)
```

## 🎯 Características

✅ **AFTER_COMMIT**: Eventos se ejecutan SOLO si el commit de la OC es exitoso
✅ **ASYNC**: Procesamiento asíncrono usando ThreadPoolExecutor (20 workers)
✅ **REQUIRES_NEW**: Nueva transacción DB independiente para cálculos
✅ **Alta concurrencia**: Soporta múltiples OC simultáneas sin bloqueos
✅ **Sin romper código existente**: Integración no invasiva

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────┐
│  POST /api/ordenes-compra/generar       │
│  Crear Orden de Compra                  │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  OrdenesCompraRepository.save()         │
│  ├─ INSERT ordenes_compra               │
│  ├─ INSERT ordenes_compra_detalles      │
│  ├─ event_dispatcher.publish()          │
│  └─ db.commit() ✅                      │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  EventDispatcher (after_commit)         │
│  Solo si commit exitoso                 │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  ThreadPoolExecutor                     │
│  Ejecución asíncrona (20 workers)       │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  ProcesarRegistroCompra (Use Case)      │
│  ├─ Nueva sesión DB (REQUIRES_NEW)      │
│  ├─ Obtener tipo de cambio SUNAT        │
│  ├─ Calcular montos consolidados        │
│  ├─ Guardar registro_compras            │
│  └─ commit() independiente              │
└─────────────────────────────────────────┘
```

## 📦 Estructura de Archivos Creados

```
app/
├── core/
│   ├── infrastructure/
│   │   └── events/
│   │       ├── __init__.py
│   │       └── event_dispatcher.py           ⭐ Sistema de eventos
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── registro_compra_service.py        ⭐ Lógica de cálculo
│   │
│   ├── use_cases/
│   │   └── registro_compra/
│   │       ├── __init__.py
│   │       └── procesar_registro_compra.py   ⭐ Handler de eventos
│   │
│   └── ports/
│       └── repositories/
│           ├── tipo_cambio_repository.py     ⭐ Port
│           └── registro_compra_repository.py ⭐ Port
│
├── adapters/
│   └── outbound/
│       └── database/
│           ├── models/
│           │   ├── tasa_cambio_sunat_model.py        ⭐ Modelo
│           │   ├── registro_compra_model.py          ⭐ Modelo
│           │   └── registro_compra_orden_model.py    ⭐ Modelo
│           │
│           └── repositories/
│               ├── tipo_cambio_repository.py          ⭐ Implementación
│               ├── registro_compra_repository.py      ⭐ Implementación
│               └── ordenes_compra_repository.py       🔄 MODIFICADO
│
└── main.py                                            🔄 MODIFICADO (lifespan)
```

## 🔄 Flujo de Procesamiento

### Escenario 1: Crear OC
1. Usuario envía request para crear OC
2. Se guarda OC en BD con detalles
3. Se publica evento `ORDEN_COMPRA_CREADA` (encolado)
4. **COMMIT exitoso** → Evento se dispara
5. En thread separado:
   - Obtener todas las OC de la cotización
   - Consultar/reutilizar tipo de cambio SUNAT
   - Calcular montos consolidados (USD → PEN, sin IGV)
   - Guardar/actualizar `registro_compras`

### Escenario 2: Editar OC (misma cotización)
1. Se actualiza OC en BD
2. Se publica evento `ORDEN_COMPRA_EDITADA`
3. **COMMIT exitoso** → Evento se dispara
4. En thread separado:
   - Usar tipo_cambio_sunat YA GUARDADO (no consultar SUNAT)
   - Recalcular montos con valores actualizados
   - Actualizar `registro_compras`

### Escenario 3: Editar OC (cambio de cotización)
1. Se actualiza OC cambiando `id_cotizacion`
2. Se publica evento con `cambio_cotizacion=True`
3. En thread separado:
   - **Cotización anterior**: Recalcular sin la OC movida o eliminar si no quedan OC
   - **Cotización nueva**: Agregar OC y recalcular

## 💰 Lógica de Cálculo

```python
# Ejemplo con 3 OC:
# OC1: 1000 PEN
# OC2: 500 USD
# OC3: 2000 PEN
# TC SUNAT: 3.75

# Paso 1: Convertir PEN a USD
total_pen = 1000 + 2000 = 3000 PEN
total_usd_convertido = 3000 / 3.75 = 800 USD

# Paso 2: Sumar en USD
total_usd = 500 + 800 = 1300 USD

# Paso 3: Convertir USD a PEN
total_pen = 1300 * 3.75 = 4875 PEN

# Paso 4: Quitar IGV (18%)
monto_sin_igv = 4875 / 1.18 = 4131.36 PEN

# Resultado:
monto_total_dolar = 1300.00
tipo_cambio_sunat = 3.75
monto_total_soles = 4875.00
monto_sin_igv = 4131.36
```

## 📊 Tablas de Base de Datos

### `tasa_cambio_sunat`
```sql
CREATE TABLE tasa_cambio_sunat (
    tasa_cambio_sunat_id INT PRIMARY KEY AUTO_INCREMENT,
    venta DECIMAL(8,3) NOT NULL,
    compra DECIMAL(8,3) NOT NULL,
    fecha DATE NOT NULL
);
```

### `registro_compras`
```sql
CREATE TABLE registro_compras (
    compra_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_cotizacion BIGINT NOT NULL,
    fecha_orden_compra DATE NOT NULL,
    monto_total_dolar DECIMAL(12,2),
    tipo_cambio_sunat DECIMAL(6,3),
    monto_total_soles DECIMAL(12,2) NOT NULL,
    monto_sin_igv DECIMAL(12,2) NOT NULL,
    tipo_empresa VARCHAR(20),
    FOREIGN KEY (id_cotizacion) REFERENCES cotizacion(id_cotizacion)
);
```

### `registro_compra_ordenes`
```sql
CREATE TABLE registro_compra_ordenes (
    orden_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    compra_id BIGINT NOT NULL,
    id_orden_compra INT NOT NULL,
    fecha_orden_compra DATE NOT NULL,
    moneda VARCHAR(3) NOT NULL,
    monto_total DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (compra_id) REFERENCES registro_compras(compra_id) ON DELETE CASCADE,
    FOREIGN KEY (id_orden_compra) REFERENCES ordenes_compra(id_orden)
);
```

## 🚀 Uso

El sistema funciona automáticamente. No requiere cambios en el código cliente:

```python
# Crear OC (como siempre)
POST /api/ordenes-compra/generar
{
    "idUsuario": 1,
    "idCotizacion": 100,
    "idCotizacionVersiones": 5,
    "consorcio": false,
    "data": [
        {
            "proveedorInfo": {...},
            "productos": [...]
        }
    ]
}

# ✅ OC se guarda
# ✅ Evento se dispara automáticamente
# ✅ registro_compras se calcula en background
# ✅ Response inmediato (no espera cálculos)
```

## ⚙️ Configuración

### Número de workers (threads)
Editar `app/core/infrastructure/events/event_dispatcher.py`:
```python
_event_dispatcher = EventDispatcher(max_workers=20)  # Ajustar según carga
```

### Timeout al apagar aplicación
Editar `app/main.py`:
```python
event_dispatcher.shutdown(wait=True, timeout=300)  # 5 minutos
```

## 🧪 Testing

Para probar el sistema:

1. **Crear OC única**
```bash
curl -X POST http://localhost:8000/api/ordenes-compra/generar \
  -H "Content-Type: application/json" \
  -d '{...}'
```

2. **Verificar logs**
```
✅ Orden 123 guardada - Evento será procesado en background
🔄 Procesando evento en thread separado: ORDEN_COMPRA_CREADA
Tipo de cambio obtenido: 3.750
✅ Cálculo completado: Soles=4875.00, Sin IGV=4131.36
✅ Registro de compra guardado: ID 45
```

3. **Consultar registro creado**
```sql
SELECT * FROM registro_compras WHERE id_cotizacion = 100;
SELECT * FROM registro_compra_ordenes WHERE compra_id = 45;
```

## ⚠️ Notas Importantes

1. **Las tablas deben existir en BD**: El sistema solo crea modelos Python, no ejecuta migraciones
2. **Tipo de cambio SUNAT**: Debe existir al menos un registro en `tasa_cambio_sunat`
3. **Campo `total` en OC**: Se calcula automáticamente sumando `precio_total` de detalles
4. **Campo `consorcio`**: Debe existir en `ordenes_compra` (agregado en implementación)
5. **Errores en eventos**: NO afectan la creación de OC (ya está commiteada)

## 🐛 Troubleshooting

### "Tipo de cambio SUNAT no disponible"
- Verificar que existe data en `tasa_cambio_sunat`
- Consultar: `SELECT * FROM tasa_cambio_sunat ORDER BY fecha DESC LIMIT 1;`

### Eventos no se ejecutan
- Verificar logs: `logger.info` debe mostrar eventos encolados
- Revisar que el commit sea exitoso (sin excepciones)

### Alto uso de CPU/memoria
- Reducir `max_workers` en EventDispatcher
- Considerar migrar a Celery para distribución

## 📈 Migración a Celery (Opcional)

Si necesitas mayor escalabilidad:

```python
# Instalar
pip install celery redis

# Configurar Celery
from celery import Celery
celery_app = Celery('crm', broker='redis://localhost:6379/0')

@celery_app.task
def procesar_registro_compra_task(event_data):
    # ... lógica
    pass

# En repository
procesar_registro_compra_task.delay(event_data)
```

## ✅ Checklist de Implementación

- [x] EventDispatcher con SQLAlchemy events
- [x] Modelos SQLAlchemy (3 tablas nuevas)
- [x] Repositorios (TipoCambio, RegistroCompra)
- [x] Servicio de cálculo de montos
- [x] Use case ProcesarRegistroCompra
- [x] Integración en OrdenesCompraRepository
- [x] Configuración lifespan en FastAPI
- [ ] Crear migraciones Alembic (pendiente)
- [ ] Insertar datos iniciales tipo_cambio_sunat (pendiente)
- [ ] Testing con múltiples OC simultáneas (pendiente)

## 📞 Soporte

Para dudas sobre la implementación, revisar:
- `app/core/infrastructure/events/event_dispatcher.py` - Sistema de eventos
- `app/core/use_cases/registro_compra/procesar_registro_compra.py` - Lógica principal
- Logs de aplicación con nivel INFO
