# ============================================
# Dockerfile para FastAPI con Playwright
# ============================================
FROM mcr.microsoft.com/playwright/python:v1.55.0-jammy

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=off

# Crear directorio de trabajo
WORKDIR /app

# Copiar e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
