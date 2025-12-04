# ====================================================================
# Dockerfile para FastAPI con Playwright (Versión con Generación Directa)
# ====================================================================

# --- ETAPA 1: Build de Dependencias ---
# En esta etapa se generan los requerimientos y se instalan.
FROM python:3.13-slim-bullseye AS builder

# Instalar pip-tools
RUN pip install pip-tools

WORKDIR /app

# Copiar requirements.in y generar requirements.txt
COPY requirements.in .
RUN pip-compile --no-header requirements.in -o requirements.txt

# Instalar dependencias de Python en un venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt


# --- ETAPA 2: Build Final de la Aplicación ---
# Esta es la imagen final que se creará.
FROM python:3.13-slim-bullseye

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=off
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/bin/ms-playwright
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Instalar dependencias del sistema para Playwright
RUN apt-get update && apt-get install -y \
    libnss3 libnspr4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libatspi2.0-0 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 \
    libasound2 libxshmfence1 \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Copiar el venv con las dependencias instaladas desde la etapa anterior
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app/requirements.txt .

# Instalar los navegadores de Playwright
RUN playwright install --with-deps

# Copiar el código de la aplicación
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
