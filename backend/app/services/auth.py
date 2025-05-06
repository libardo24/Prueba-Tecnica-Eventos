from sqlalchemy import select, insert
from app.models.usuarios import usuarios_table, set_password, check_password
from app.schemas.usuarios import UsuarioSchema
from app import db
import jwt
from datetime import datetime, timezone, timedelta
from app.core.config import settings
from marshmallow import ValidationError
from app.schemas.usuarios import UsuarioCreateSchema


def register_user_service(data):
    try:
        # Validar los datos primero
        validated_data = UsuarioCreateSchema().load(data)
        
        email = validated_data['email']
        password = validated_data['password']

        # Verificar si el usuario ya existe
        stmt = select(usuarios_table).where(usuarios_table.c.email == email)
        existing_user = db.session.execute(stmt).fetchone()
        if existing_user:
            return {"message": "Email already exists"}, 400

        # Crear un nuevo usuario
        hashed_password = set_password(password)
        stmt = insert(usuarios_table).values(email=email, password_hash=hashed_password)
        db.session.execute(stmt)
        db.session.commit()

        return {"message": "User created successfully"}, 201

    except ValidationError as err:
        return {"errors": err.messages}, 400
    except Exception as e:
        return {"message": f"Error creating user: {str(e)}"}, 500

def login_user_service(data):
    email = data['email']
    password = data['password']

    # Buscar el usuario por email
    stmt = select(usuarios_table).where(usuarios_table.c.email == email)
    user = db.session.execute(stmt).fetchone()
    if not user or not check_password(user.password_hash, password):
        return {"message": "Invalid credentials"}, 401

    # Crear un JWT token
    token = jwt.encode({
        'sub': str(user.id),
        'exp': datetime.now(timezone.utc) + timedelta(hours=10)
    }, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)

    # Serializar los datos del usuario
    usuario_schema = UsuarioSchema()
    usuario_data = usuario_schema.dump(dict(user._mapping))

    return {"token": token, "user": usuario_data}, 200