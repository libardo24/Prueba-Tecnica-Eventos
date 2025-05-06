from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api
from flask_cors import CORS  # Añadir import
from dotenv import load_dotenv
import os

# Cargar las variables del archivo .env
load_dotenv()

# Instancia global de SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configuración de la base de datos (PostgreSQL)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Habilitar CORS
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173"]}})

    db.init_app(app)

    # Configuración de Flask-RESTx
    api = Api(
        app,
        version="1.0",
        title="Mis Eventos API",
        description="Documentación de la API para la aplicación Mis Eventos",
        doc="/docs"  # Ruta donde estará la documentación Swagger
    )

    # Registrar namespaces
    from app.routes.eventos import evento_ns
    from app.routes.auth import auth_ns
    from app.routes.sesiones import sesion_ns
    api.add_namespace(evento_ns, path="/api/eventos")
    api.add_namespace(auth_ns, path="/api/auth")
    api.add_namespace(sesion_ns, path="/api/sesiones")

    return app