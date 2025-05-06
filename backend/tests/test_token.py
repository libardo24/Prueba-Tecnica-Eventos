import pytest
import jwt
from app.core.config import settings
from app.core.auth import decode_jwt, token_required
from unittest.mock import patch

# Pruebas para decode_jwt
def test_decode_jwt_success():
    # Simular un token válido
    token = "valid.token"
    decoded_data = {"sub": "1"}
    with patch('jwt.decode', return_value=decoded_data) as mock_decode:
        result = decode_jwt(token)
    
    assert result == decoded_data
    mock_decode.assert_called_once_with(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])

def test_decode_jwt_expired():
    # Simular un token expirado
    token = "expired.token"
    with patch('jwt.decode', side_effect=jwt.ExpiredSignatureError):
        with pytest.raises(ValueError, match="Token has expired"):
            decode_jwt(token)

def test_decode_jwt_invalid():
    # Simular un token inválido
    token = "invalid.token"
    with patch('jwt.decode', side_effect=jwt.InvalidTokenError):
        with pytest.raises(ValueError, match="Invalid token"):
            decode_jwt(token)

# Pruebas para token_required
def test_token_required_missing_token(app):
    with app.test_request_context('/', headers={}):
        @token_required
        def dummy_route(*args, **kwargs):
            return {"success": True}, 200
        
        result, status_code = dummy_route()
    
    assert status_code == 403
    assert result["message"] == "Authentication token is missing!"

def test_token_required_invalid_token(app):
    with app.test_request_context('/', headers={"Authorization": "Bearer invalid.token"}):
        with patch('app.core.auth.decode_jwt', side_effect=ValueError("Invalid token")):
            @token_required
            def dummy_route(*args, **kwargs):
                return {"success": True}, 200
            
            result, status_code = dummy_route()
    
    assert status_code == 403
    assert result["message"] == "Invalid token"

def test_token_required_success(app):
    with app.test_request_context('/', headers={"Authorization": "Bearer valid.token"}):
        decoded_data = {"sub": "1"}
        with patch('app.core.auth.decode_jwt', return_value=decoded_data):
            @token_required
            def dummy_route(*args, **kwargs):
                return {"user_id": kwargs["current_user"]["id"]}, 200
            
            result, status_code = dummy_route()
    
    assert status_code == 200
    assert result["user_id"] == 1

def test_token_required_invalid_sub(app):
    with app.test_request_context('/', headers={"Authorization": "Bearer valid.token"}):
        decoded_data = {"sub": "not-an-integer"}
        with patch('app.core.auth.decode_jwt', return_value=decoded_data):
            @token_required
            def dummy_route(*args, **kwargs):
                return {"success": True}, 200

            result, status_code = dummy_route()

    assert status_code == 403
    assert result["message"] == "Invalid token: user ID must be an integer"  # Cambiar el mensaje esperado