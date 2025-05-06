import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="flask_restx")
import pytest
from unittest.mock import patch
from flask import Flask
from app import db

# Fixture para la aplicación Flask
@pytest.fixture
def app():
    app = Flask(__name__)
    return app

# Fixture para el cliente de prueba de Flask
@pytest.fixture
def client(app):
    return app.test_client()

# Fixture para simular la sesión de la base de datos
@pytest.fixture
def mock_db_session():
    with patch('app.db.session') as mock:
        yield mock

# Fixture para datos de usuario comunes
@pytest.fixture
def user_data():
    return {
        "email": "test@example.com",
        "password": "securepassword123"
    }

# Fixture para un usuario existente simulado
@pytest.fixture
def existing_user():
    from unittest.mock import MagicMock
    user = MagicMock()
    user._mapping = {
        "id": 1,
        "email": "existing@example.com",
        "password_hash": "hashedpassword"
    }
    user.id = 1  # Configurar el atributo id explícitamente
    return user