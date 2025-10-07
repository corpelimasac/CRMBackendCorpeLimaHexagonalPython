# 🌍 Guía de Configuración por Entornos

Este proyecto soporta múltiples entornos: **desarrollo**, **producción** y **staging**.

---

## 📁 Archivos de Configuración

```
.env.example         → Plantilla de ejemplo
.env.development     → Configuración de desarrollo (SQLite local)
.env.production      → Configuración de producción (MySQL Railway/Cloud)
.env                 → Archivo activo (git ignorado)
```

---

## 🚀 Configuración por Entorno

### **1️⃣ Desarrollo Local (SQLite)**

**Características:**
- Base de datos local SQLite (no requiere MySQL)
- Debug activado
- CORS abierto (*)
- Menos workers (5)

**Configurar:**

```bash
# Copiar archivo de desarrollo
cp .env.development .env

# O crear manualmente .env con:
ENVIRONMENT=development
DEBUG=True
DATABASE_URL=sqlite:///./crm_local.db
CORS_ORIGINS=*
EVENTO_FINANCIERO_MAX_WORKERS=5
```

**Ejecutar:**

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Salida esperada:**

```
============================================================
🚀 Iniciando CRM Backend - Development
📦 Versión: 1.0.0
🌍 Entorno: DEVELOPMENT
🐛 Debug: True
🗄️  Base de datos: ./crm_local.db
============================================================
✅ EventDispatcher inicializado con 5 workers
```

---

### **2️⃣ Desarrollo Local (MySQL)**

**Características:**
- Base de datos MySQL local
- Debug activado
- Mismo comportamiento que producción pero local

**Configurar:**

```bash
# Crear .env
ENVIRONMENT=development
DEBUG=True
DATABASE_URL=mysql+pymysql://root:tu_password@localhost:3306/crm_dev
ASYNC_DATABASE_URL=mysql+aiomysql://root:tu_password@localhost:3306/crm_dev
CORS_ORIGINS=*
EVENTO_FINANCIERO_MAX_WORKERS=10
```

**Ejecutar MySQL local:**

```bash
# Con Docker
docker run -d \
  --name mysql-crm \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=crm_dev \
  -p 3306:3306 \
  mysql:8.0

# O instalar MySQL directamente
```

---

### **3️⃣ Producción (Railway/Cloud)**

**Características:**
- Base de datos MySQL en la nube
- Debug desactivado
- CORS restringido a dominios específicos
- Más workers (20)

**Configurar:**

```bash
# Copiar archivo de producción
cp .env.production .env

# Editar .env con credenciales reales:
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=mysql+pymysql://usuario:password@host.railway.app:3306/railway
ASYNC_DATABASE_URL=mysql+aiomysql://usuario:password@host.railway.app:3306/railway
CORS_ORIGINS=https://tudominio.com,https://admin.tudominio.com
EVENTO_FINANCIERO_MAX_WORKERS=20
```

**Ejecutar localmente (probando con DB de producción):**

```bash
# ⚠️ CUIDADO: Esto usa la base de datos de producción
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Desplegar en Railway:**

```bash
# Railway leerá .env automáticamente o configurar variables en el panel
railway up
```

---

## 🐳 Docker

### **Desarrollo con Docker**

```bash
# Usar DB local en el contenedor
docker build -t crm-backend .

docker run -d \
  -p 8000:8000 \
  -e ENVIRONMENT=development \
  -e DATABASE_URL=sqlite:///./crm_local.db \
  --name crm-backend \
  crm-backend
```

### **Producción con Docker**

```bash
# Usar DB de producción
docker run -d \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e DATABASE_URL=mysql+pymysql://usuario:password@host.railway.app:3306/railway \
  -e CORS_ORIGINS=https://tudominio.com \
  --name crm-backend \
  crm-backend
```

### **Docker Compose (Multi-entorno)**

Crear `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # Desarrollo
  backend-dev:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - DATABASE_URL=sqlite:///./crm_local.db
      - DEBUG=True
    volumes:
      - ./app:/app/app
    command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

  # Producción
  backend-prod:
    build: .
    ports:
      - "8001:8000"
    env_file:
      - .env.production
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Ejecutar:

```bash
# Desarrollo
docker-compose up backend-dev

# Producción
docker-compose up backend-prod
```

---

## 🔧 Variables de Entorno Disponibles

| Variable | Desarrollo | Producción | Descripción |
|----------|-----------|------------|-------------|
| `ENVIRONMENT` | `development` | `production` | Entorno de ejecución |
| `DEBUG` | `True` | `False` | Modo debug |
| `DATABASE_URL` | SQLite local | MySQL cloud | URL de conexión principal |
| `ASYNC_DATABASE_URL` | SQLite async | MySQL async | URL async (opcional) |
| `CORS_ORIGINS` | `*` | Dominios específicos | Orígenes CORS permitidos |
| `EVENTO_FINANCIERO_MAX_WORKERS` | `5` | `20` | Workers para eventos |
| `EVENTO_FINANCIERO_TIMEOUT` | `60` | `300` | Timeout al apagar (segundos) |

---

## 🔍 Verificar Configuración Actual

### **Opción 1: Logs al iniciar**

Al ejecutar la aplicación verás:

```
============================================================
🚀 Iniciando CRM Backend - Production
📦 Versión: 1.0.0
🌍 Entorno: PRODUCTION
🐛 Debug: False
🗄️  Base de datos: host.railway.app:3306/railway
============================================================
```

### **Opción 2: Endpoint de Health**

```bash
curl http://localhost:8000/api/health
```

Respuesta:

```json
{
  "status": "healthy",
  "environment": "production",
  "database": "connected"
}
```

---

## 🛠️ Mejores Prácticas

### ✅ **DO's**

1. **Nunca commitear `.env`** (está en `.gitignore`)
2. **Usar `.env.development` para desarrollo local**
3. **Configurar variables en Railway/Cloud para producción**
4. **Probar localmente con DB de dev antes de desplegar**
5. **Revisar logs al iniciar para confirmar entorno correcto**

### ❌ **DON'Ts**

1. **Nunca usar `ENVIRONMENT=production` con SQLite**
2. **No dejar `DEBUG=True` en producción**
3. **No usar `CORS_ORIGINS=*` en producción**
4. **No commitear credenciales en archivos de configuración**

---

## 🐛 Solución de Problemas

### **Error: "No se pudo conectar a la base de datos"**

```bash
# Verificar DATABASE_URL
echo $DATABASE_URL

# Probar conexión manual
python -c "from sqlalchemy import create_engine; engine = create_engine('$DATABASE_URL'); engine.connect()"
```

### **Error: "Módulo no encontrado"**

```bash
# Reinstalar dependencias
pip install -r requirements.txt
```

### **Base de datos no se crea**

```bash
# Para SQLite, verificar que el directorio existe
touch crm_local.db

# Para MySQL, crear base de datos manualmente
mysql -u root -p -e "CREATE DATABASE crm_dev;"
```

---

## 📚 Recursos

- [Pydantic Settings](https://docs.pydantic.dev/latest/usage/settings/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [FastAPI Environments](https://fastapi.tiangolo.com/advanced/settings/)
- [Railway Docs](https://docs.railway.app/)

---

## 🚨 Seguridad

**Variables sensibles para producción:**

```bash
# Configurar en Railway/Cloud (NO en archivos):
railway variables set DATABASE_URL=mysql+pymysql://...
railway variables set CORS_ORIGINS=https://tudominio.com
```

**Rotar credenciales periódicamente:**

1. Cambiar password de base de datos
2. Actualizar `DATABASE_URL`
3. Redesplegar aplicación
