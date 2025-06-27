# Usa una imagen oficial de Python
FROM python:3.11-slim

# Evita errores por variables de entorno no definidas
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=off

# Crea el directorio de la app
WORKDIR /app

# Copia los requirements
COPY requirements.txt .

# Instala dependencias (ignora errores)
RUN pip install --upgrade pip && \
    pip install -r requirements.txt || true

# Copia el resto del código
COPY . .

# Expone el puerto (ajusta si usas otro)
EXPOSE 8000

# Comando para arrancar FastAPI con Uvicorn, ignora errores de migración, etc.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 || true"]