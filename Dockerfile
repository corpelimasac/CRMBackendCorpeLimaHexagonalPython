# Usar imagen base con Chrome ya instalado (RECOMENDADO)
FROM selenium/standalone-chrome:latest

# Cambiar al usuario root temporalmente para instalar dependencias
USER root

# Instalar Python 3.11 y pip
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-pip \
    python3.11-venv \
    python3.11-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear enlaces simbólicos para python y pip
RUN ln -sf /usr/bin/python3.11 /usr/bin/python \
    && ln -sf /usr/bin/python3.11 /usr/bin/python3 \
    && ln -sf /usr/bin/pip3 /usr/bin/pip

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=off

# Crear directorio de la aplicación
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear usuario para la aplicación
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app

# Exponer puerto
EXPOSE 8000

# Cambiar al usuario de la aplicación
USER appuser

# Comando para iniciar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]