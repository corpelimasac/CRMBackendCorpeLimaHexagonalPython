# 1. Usa una imagen base específica y estable (Debian Bookworm)
FROM python:3.11-bookworm

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=off

# 2. Instalar dependencias del sistema y Google Chrome
# Actualiza la lista de paquetes e instala dependencias que Chrome necesita
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    # Dependencias clave para que Chrome funcione
    libglib2.0-0 \
    libnss3 \
    # libgconf-2-4  <-- SE HA ELIMINADO ESTA LÍNEA OBSOLETA
    libfontconfig1 \
    libx11-6 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libsm6 \
    libxrandr2 \
    libxrender1 \
    libcups2 \
    libdbus-1-3 \
    libxss1 \
    libxtst6 \
    libasound2 \
    --no-install-recommends

# Descarga y añade la clave de Google
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# Añade el repositorio de Chrome a las fuentes del sistema
RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list

# Actualiza de nuevo e instala Google Chrome Stable
RUN apt-get update \
    && apt-get install -y google-chrome-stable --no-install-recommends \
    # Limpia la caché para reducir el tamaño de la imagen
    && rm -rf /var/lib/apt/lists/*

# Crea el directorio de la app
WORKDIR /app

# Copia e instala los requerimientos de Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia el resto del código
COPY . .

# Expone el puerto
EXPOSE 8000

# Comando para arrancar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]