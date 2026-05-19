# Dockerfile para el proyecto "Servicio Telemático Dockerizado"
#
# Este archivo contiene instrucciones para crear una imagen Docker
# reproducible del servicio Flask. La imagen se basa en Python slim
# para reducir el tamaño. La aplicación escucha en el puerto 5000.

# Utilizar una imagen base ligera de Python
FROM python:3.10-slim AS base

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Crear directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar archivo de dependencias primero para aprovechar el cache
COPY requirements.txt /app/

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . /app

# Exponer el puerto que utiliza la aplicación Flask
EXPOSE 5000

# Comando por defecto para ejecutar la aplicación
CMD ["python", "app.py"]