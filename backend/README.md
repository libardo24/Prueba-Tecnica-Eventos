📦 Backend - Mis Eventos
Este es el backend de la aplicación Mis Eventos, desarrollado con Flask y PostgreSQL. Proporciona una API RESTful para gestionar usuarios, eventos y sesiones.

📁 Estructura del proyecto

backend/
├── app/
│   ├── __init__.py        # Configuración principal de Flask
│   ├── models/            # Modelos de la base de datos
│   ├── routes/            # Rutas de la API
│   ├── services/          # Lógica de negocio
│   ├── schemas/           # Esquemas de validación
│   └── main.py            # Punto de entrada de la aplicación
├── tests                  # test unitarios
├── Alembic/               # Migraciones de la base de datos (Alembic)
├── Dockerfile             # Configuración de Docker para el backend
├── pyproject.toml         # Configuración de Poetry
└── README.md              # Este archivo
✅ Requisitos previos
Asegúrate de tener instalados los siguientes programas:

Docker y Docker Compose

Python 3.12 (opcional si no usas Docker)

⚙️ Configuración
1. Clonar el repositorio
git clone https://github.com/libardo24/Prueba-Tecnica-Eventos.git
cd Prueba-Tecnica-Eventos/backend

2. Crear archivo .env
Crea un archivo .env en el directorio backend con el siguiente contenido:

JWT_SECRET_KEY="super-secret"
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/mis_eventos


🚀 Ejecución
Opción 1: Usando Docker
Desde el directorio raíz del proyecto:


docker-compose up --build
Esto iniciará los servicios de Flask y PostgreSQL.

Accede a la API en:
👉 http://localhost:5000

Opción 2: Sin Docker (opcional)
1. Instalar dependencias
Asegúrate de tener Python 3.12 y Poetry instalado.


cd backend
poetry install
2. Ejecutar la aplicación

poetry run flask run
La API estará disponible en:
👉 http://localhost:5000

3. Activar el entorno virtual (opcional)

source $(poetry env info --path)/bin/activate
📘 Documentación de la API
Este proyecto incluye documentación interactiva generada con Swagger UI.
Una vez que la API esté corriendo, accede a la documentación en:

👉 http://localhost:5000/docs


las coverturas de los test se ubican en la carpeta htmlcov