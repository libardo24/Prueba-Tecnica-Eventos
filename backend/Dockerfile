# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copiar todos los archivos del backend al contenedor
COPY . /app/

# Instalar Poetry y dependencias
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-interaction

# Instalar netcat para esperar a la DB
RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean

# Ejecutar migraciones y luego levantar el servidor Flask
CMD ["sh", "-c", "while ! nc -z db 5432; do sleep 1; done; alembic upgrade head && flask run --host=0.0.0.0"]


