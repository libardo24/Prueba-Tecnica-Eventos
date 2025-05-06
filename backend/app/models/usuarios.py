from sqlalchemy import Table, Column, Integer, String
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.shared import metadata

# Definición de la tabla usuarios
usuarios_table = Table(
    'usuarios', metadata,
    Column('id', Integer, primary_key=True),
    Column('email', String(120), unique=True, nullable=False),
    Column('password_hash', String(256), nullable=False)
)

# Funciones auxiliares para manejar contraseñas
def set_password(password):
    """Genera un hash de la contraseña."""
    return generate_password_hash(password)

def check_password(hashed_password, password):
    """Verifica si la contraseña proporcionada coincide con el hash almacenado."""
    return check_password_hash(hashed_password, password)
