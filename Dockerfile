# ====================================================================
# Dockerfile para FastAPI con Playwright (Versión con Verificación)
# ====================================================================

# --- ETAPA 1: Verificador de Dependencias ---
# Esta etapa solo se usa para verificar que requirements.txt esté actualizado.
FROM python:3.11-slim-bullseye AS verifier

# Instalar pip-tools
RUN pip install pip-tools

WORKDIR /app

# Copiar solo los archivos de requerimientos
COPY requirements.in .
COPY requirements.txt .

# Verificar si requirements.txt está sincronizado con requirements.in
# Si no lo está, el comando 'diff' fallará y detendrá el build.
RUN pip-compile --quiet requirements.in -o - | diff requirements.txt - || \
    (echo "ERROR: requirements.txt está desactualizado." && \
     echo "Por favor, ejecuta 'pip-compile --upgrade' y commitea los cambios." && \
     exit 1)


# --- ETAPA 2: Build Final de la Aplicación ---
# Esta es la imagen final que se creará si la verificación pasa.
FROM python:3.11-slim-bullseye

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=off
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/bin/ms-playwright

WORKDIR /app

# Instalar dependencias del sistema para Playwright
RUN apt-get update && apt-get install -y \
    libnss3 libnspr4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libatspi2.0-0 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 \
    libasound2 libxshmfence1 \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Copiar el requirements.txt verificado desde la etapa anterior
COPY --from=verifier /app/requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Instalar los navegadores de Playwright
RUN playwright install --with-deps

# Copiar el código de la aplicación
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
