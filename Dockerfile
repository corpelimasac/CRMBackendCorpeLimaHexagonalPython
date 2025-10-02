# ============================================
# ETAPA 1: Imagen base con Chrome pre-instalado
# ============================================
FROM zenika/alpine-chrome:with-chromedriver AS chrome-base

# ============================================
# ETAPA 2: Imagen de producción optimizada
# ============================================
FROM python:3.11-alpine

# Variables de entorno optimizadas
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=off
ENV CHROME_BIN=/usr/bin/chromium-browser
ENV CHROME_PATH=/usr/bin/chromium-browser
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Instalar dependencias mínimas necesarias para Python y Chrome
RUN apk add --no-cache \
    # Dependencias de Chrome/Chromium
    chromium \
    chromium-chromedriver \
    # Dependencias de compilación para algunos paquetes Python
    gcc \
    musl-dev \
    libffi-dev \
    # Utilidades
    bash \
    && ln -s /usr/bin/chromium-browser /usr/bin/google-chrome

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