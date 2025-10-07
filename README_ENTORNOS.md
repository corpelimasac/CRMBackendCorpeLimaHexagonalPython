# 🚀 Guía Rápida - Configuración de Entornos

## ⚡ Inicio Rápido

### **Desarrollo Local (Recomendado para empezar)**

```bash
# 1. Cambiar a entorno de desarrollo
./switch-env.sh dev          # Linux/Mac
switch-env.bat dev           # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar aplicación
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ **Salida esperada:**
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

### **Producción**

```bash
# 1. Cambiar a entorno de producción
./switch-env.sh prod         # Linux/Mac
switch-env.bat prod          # Windows

# 2. Editar .env con credenciales reales
nano .env
# DATABASE_URL=mysql+pymysql://usuario:password@host:3306/db

# 3. Ejecutar aplicación
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 📂 Archivos Importantes

| Archivo | Descripción |
|---------|-------------|
| `.env.development` | Configuración de desarrollo (SQLite) |
| `.env.production` | Configuración de producción (MySQL) |
| `.env` | Archivo activo (generado por scripts) |
| `switch-env.sh` | Script para cambiar entornos (Linux/Mac) |
| `switch-env.bat` | Script para cambiar entornos (Windows) |
| `CONFIGURACION_ENTORNOS.md` | Guía completa de configuración |

---

## 🔧 Cambiar Entorno Manualmente

Si no quieres usar los scripts:

```bash
# Desarrollo
cp .env.development .env

# Producción
cp .env.production .env
```

---

## 📊 Verificar Entorno Actual

```bash
# Ver configuración
cat .env | grep ENVIRONMENT

# O ejecutar la app y ver los logs de inicio
```

---

## 🌍 Entornos Disponibles

### **Development** (Desarrollo)
- ✅ Base de datos: SQLite local
- ✅ Debug: Activado
- ✅ CORS: Abierto (*)
- ✅ Workers: 5

### **Production** (Producción)
- ✅ Base de datos: MySQL cloud
- ✅ Debug: Desactivado
- ✅ CORS: Restringido
- ✅ Workers: 20

---

## 🐛 Problemas Comunes

### **Error: "No se encuentra .env.development"**
```bash
# Copiar desde ejemplo
cp .env.example .env.development
```

### **Error: "Permiso denegado al ejecutar script"**
```bash
# Dar permisos (Linux/Mac)
chmod +x switch-env.sh
```

### **Error: "Base de datos no conecta"**
```bash
# Verificar DATABASE_URL en .env
cat .env | grep DATABASE_URL
```

---

## 📚 Documentación Completa

Para más detalles, ver:
- [CONFIGURACION_ENTORNOS.md](CONFIGURACION_ENTORNOS.md) - Guía completa de configuración
- [EVENTOS_REGISTRO_COMPRAS.md](EVENTOS_REGISTRO_COMPRAS.md) - Sistema de eventos asíncronos

---

## ⚙️ Variables de Entorno Clave

```bash
# Obligatorias
ENVIRONMENT=development              # development, production, staging
DATABASE_URL=sqlite:///./crm.db      # URL de conexión a BD

# Opcionales
DEBUG=True                           # Modo debug
CORS_ORIGINS=*                       # Orígenes CORS permitidos
EVENTO_FINANCIERO_MAX_WORKERS=20     # Workers para eventos
```

---

## 🚨 Seguridad

⚠️ **NUNCA commitear archivos `.env` con credenciales reales**

✅ **Usar variables de entorno en Railway/Cloud:**
```bash
railway variables set DATABASE_URL=mysql+pymysql://...
railway variables set CORS_ORIGINS=https://tudominio.com
```

---

## 📞 Soporte

Si tienes problemas:
1. Verifica que `.env` existe y tiene las variables correctas
2. Revisa los logs al iniciar la aplicación
3. Consulta `CONFIGURACION_ENTORNOS.md` para guía detallada
