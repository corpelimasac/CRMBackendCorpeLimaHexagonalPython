# Usa una imagen oficial de Python
FROM python:3.11-slim

# Evita errores por variables de entorno no definidas
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=off

# Variables de entorno para Chrome
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROME_DRIVER=/usr/bin/chromedriver

# Instalar dependencias del sistema necesarias para Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    # Dependencias de Chrome
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libvulkan1 \
    && rm -rf /var/lib/apt/lists/*

# Instalar Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio para ChromeDriver
RUN mkdir -p /opt/chromedriver

# Instalar ChromeDriver compatible
RUN CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) \
    && wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip" \
    && unzip /tmp/chromedriver.zip -d /opt/chromedriver \
    && rm /tmp/chromedriver.zip \
    && chmod +x /opt/chromedriver/chromedriver \
    && ln -fs /opt/chromedriver/chromedriver /usr/bin/chromedriver

# Crea el directorio de la app
WORKDIR /app

# Copia los requirements
COPY requirements.txt .

# Instala dependencias de Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copia el resto del código
COPY . .

# Crear usuario no-root para ejecutar Chrome de forma segura
RUN groupadd -r chromeuser && useradd -r -g chromeuser -G audio,video chromeuser \
    && mkdir -p /home/chromeuser/Downloads \
    && chown -R chromeuser:chromeuser /home/chromeuser \
    && chown -R chromeuser:chromeuser /app

# Expone el puerto
EXPOSE 8000

# Cambiar al usuario no-root
USER chromeuser

# Comando para arrancar FastAPI con Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]