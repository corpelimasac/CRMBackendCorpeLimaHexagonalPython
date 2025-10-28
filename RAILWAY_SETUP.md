# Configuración para Railway

## Variables de Entorno Requeridas

Railway proporciona automáticamente `DATABASE_URL` cuando agregas una base de datos PostgreSQL. El código ahora extrae automáticamente todas las configuraciones de base de datos de esta variable.

### Variables Mínimas Requeridas

Solo necesitas configurar estas variables en Railway:

1. **DATABASE_URL** - Proporcionada automáticamente por Railway al agregar PostgreSQL
2. **AWS_ACCESS_KEY_ID** - Tu clave de acceso de AWS
3. **AWS_SECRET_ACCESS_KEY** - Tu clave secreta de AWS
4. **AWS_BUCKET_NAME** - Nombre de tu bucket S3 (ejemplo: bucketcorpelima)

### Variables Opcionales

Estas tienen valores por defecto pero puedes personalizarlas:

- **ENVIRONMENT** - `production` (recomendado para Railway)
- **DEBUG** - `False` (recomendado para producción)
- **CORS_ORIGINS** - `*` (permite todos los orígenes)
- **AWS_REGION** - `us-east-1` (región de AWS)

## Pasos para Configurar en Railway

1. Ve a tu proyecto en Railway
2. Selecciona tu servicio
3. Ve a la pestaña "Variables"
4. Agrega las variables de AWS:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_BUCKET_NAME`
5. (Opcional) Agrega `ENVIRONMENT=production`
6. Railway ya proporciona `DATABASE_URL` automáticamente

## ¿Qué hace el código automáticamente?

Cuando solo tienes `DATABASE_URL`, el código:
- Extrae `database_host`, `database_port`, `database_user`, `database_password`, `database_name`
- Crea `async_database_url` reemplazando `postgresql://` por `postgresql+asyncpg://`

Ejemplo de `DATABASE_URL` de Railway:
```
postgresql://postgres:password@containers-us-west-123.railway.app:5432/railway
```

Se convierte automáticamente en:
- `async_database_url`: `postgresql+asyncpg://postgres:password@containers-us-west-123.railway.app:5432/railway`
- `database_host`: `containers-us-west-123.railway.app`
- `database_port`: `5432`
- `database_user`: `postgres`
- `database_password`: `password`
- `database_name`: `railway`
