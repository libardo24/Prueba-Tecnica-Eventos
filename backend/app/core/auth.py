from functools import wraps
from flask import request
import jwt
from app.core.config import settings

def decode_jwt(token):
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
        if not token:
            return {"message": "Authentication token is missing!"}, 403

        try:
            data = decode_jwt(token)
            sub = data.get("sub")
            if not sub:
                return {"message": "Invalid token: missing user ID"}, 403
            try:
                user_id = int(sub)  # Asegurarse de que sub sea un entero
            except (ValueError, TypeError):
                return {"message": "Invalid token: user ID must be an integer"}, 403
            current_user = {"id": user_id}
        except ValueError as e:
            return {"message": str(e)}, 403
        except Exception:
            return {"message": "Authentication failed!"}, 403

        kwargs['current_user'] = current_user
        return f(*args, **kwargs)
    return decorator