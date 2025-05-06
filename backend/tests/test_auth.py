import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone, timedelta
import jwt
from app.services.auth import register_user_service, login_user_service
from app.core.config import settings

# Fixtures
@pytest.fixture
def mock_db_session():
    with patch('app.db.session') as mock:
        yield mock

@pytest.fixture
def user_data():
    return {
        "email": "test@example.com",
        "password": "securepassword123"
    }

@pytest.fixture
def existing_user():
    return MagicMock(
        _mapping={
            "id": 1,
            "email": "existing@example.com",
            "password_hash": "hashedpassword"
        }
    )

@pytest.fixture
def mock_jwt_encode():
    with patch('jwt.encode') as mock:
        mock.return_value = "mocked.jwt.token"
        yield mock

# Pruebas para register_user_service
def test_register_user_success(mock_db_session, user_data):
    # Configurar el mock para simular que no existe el usuario
    mock_db_session.execute.return_value.fetchone.return_value = None
    
    result, status_code = register_user_service(user_data)
    
    assert status_code == 201
    assert result["message"] == "User created successfully"
    mock_db_session.execute.assert_called()
    mock_db_session.commit.assert_called_once()

def test_register_user_existing_email(mock_db_session, user_data, existing_user):
    # Configurar el mock para simular que el usuario ya existe
    mock_db_session.execute.return_value.fetchone.return_value = existing_user
    
    result, status_code = register_user_service(user_data)
    
    assert status_code == 400
    assert result["message"] == "Email already exists"
    mock_db_session.commit.assert_not_called()

def test_register_user_invalid_data(mock_db_session):
    # Datos inválidos (falta password)
    invalid_data = {"email": "test@example.com"}
    
    result, status_code = register_user_service(invalid_data)
    
    assert status_code == 400
    assert "errors" in result
    assert "password" in result["errors"]  # Verificar que el error es por password faltante
    mock_db_session.execute.assert_not_called()

# Pruebas para login_user_service
def test_login_user_success(mock_db_session, user_data, existing_user, mock_jwt_encode):
    # Configurar mocks
    mock_db_session.execute.return_value.fetchone.return_value = existing_user
    with patch('app.services.auth.check_password', return_value=True):
        result, status_code = login_user_service(user_data)
    
    assert status_code == 200
    assert "token" in result
    assert "user" in result
    assert result["token"] == "mocked.jwt.token"
    mock_jwt_encode.assert_called_once()

def test_login_user_invalid_credentials(mock_db_session, user_data):
    # Configurar mock para simular usuario no encontrado
    mock_db_session.execute.return_value.fetchone.return_value = None
    
    result, status_code = login_user_service(user_data)
    
    assert status_code == 401
    assert result["message"] == "Invalid credentials"

def test_login_user_wrong_password(mock_db_session, user_data, existing_user):
    # Configurar mocks
    mock_db_session.execute.return_value.fetchone.return_value = existing_user
    with patch('app.services.auth.check_password', return_value=False):
        result, status_code = login_user_service(user_data)
    
    assert status_code == 401
    assert result["message"] == "Invalid credentials"

def test_login_user_token_generation(mock_db_session, user_data, existing_user):
    # Configurar mocks
    existing_user.id = 1  # Asegurarse de que existing_user.id devuelva 1
    mock_db_session.execute.return_value.fetchone.return_value = existing_user
    # Simular el datetime para evitar problemas de tiempo
    fixed_time = datetime.now(timezone.utc)
    with patch('app.services.auth.datetime') as mock_datetime:
        mock_datetime.now.return_value = fixed_time
        with patch('app.services.auth.check_password', return_value=True):
            with patch('jwt.encode') as jwt_mock:
                jwt_mock.return_value = "generated.token"
                result, status_code = login_user_service(user_data)

    assert status_code == 200
    assert result["token"] == "generated.token"

    # Verificar que se llamó a jwt.encode con los parámetros correctos
    expected_payload = {
        'sub': '1',  # user.id como string
        'exp': fixed_time + timedelta(hours=10)  # Usar el tiempo simulado
    }
    jwt_mock.assert_called_once_with(
        expected_payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

# Pruebas para casos extremos
def test_register_user_empty_password(mock_db_session):
    invalid_data = {"email": "test@example.com", "password": ""}
    
    result, status_code = register_user_service(invalid_data)
    
    assert status_code == 400
    assert "errors" in result  # Cambiar "message" por "errors"
    assert "password" in result["errors"]
    assert "La contraseña debe tener entre 6 y 128 caracteres" in result["errors"]["password"]

def test_login_user_empty_fields(mock_db_session):
    invalid_data = {"email": "", "password": ""}
    
    result, status_code = login_user_service(invalid_data)
    
    assert status_code == 401
    assert result["message"] == "Invalid credentials"

def test_register_user_empty_data(mock_db_session):
    result, status_code = register_user_service({})
    assert status_code == 400
    assert "email" in result["errors"]
    assert "password" in result["errors"]

def test_register_user_invalid_email(mock_db_session):
    result, status_code = register_user_service({
        "email": "not-an-email",
        "password": "validpass123"
    })
    assert status_code == 400
    assert "email" in result["errors"]