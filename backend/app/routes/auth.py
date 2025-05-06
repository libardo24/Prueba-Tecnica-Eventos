from flask_restx import Namespace, Resource, fields
from marshmallow import ValidationError
from app.schemas.usuarios import UsuarioCreateSchema
from app.services.auth import register_user_service, login_user_service

# Crear un namespace para las rutas de autenticación
auth_ns = Namespace("auth", description="Operaciones relacionadas con la autenticación")

# Modelo de entrada para registrar un usuario
register_model = auth_ns.model("Register", {
    "email": fields.String(required=True, description="Correo electrónico del usuario"),
    "password": fields.String(required=True, description="Contraseña del usuario")
})

# Modelo de entrada para iniciar sesión
login_model = auth_ns.model("Login", {
    "email": fields.String(required=True, description="Correo electrónico del usuario"),
    "password": fields.String(required=True, description="Contraseña del usuario")
})

# Rutas
@auth_ns.route("/register")
class RegisterUser(Resource):
    @auth_ns.expect(register_model)
    @auth_ns.response(201, "Usuario registrado exitosamente")
    @auth_ns.response(400, "Error en los datos proporcionados")
    def post(self):
        """Registrar un nuevo usuario"""
        json_data = auth_ns.payload  # Obtiene los datos enviados en el cuerpo de la solicitud

        # Validar los datos de entrada con el esquema
        try:
            data = UsuarioCreateSchema().load(json_data)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        # Pasar los datos validados al servicio
        return register_user_service(data)


@auth_ns.route("/login")
class LoginUser(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.response(200, "Inicio de sesión exitoso", model=auth_ns.model("LoginResponse", {
        "token": fields.String(description="Token JWT generado"),
        "user": fields.Raw(description="Información del usuario autenticado")
    }))
    @auth_ns.response(400, "Error en los datos proporcionados")
    @auth_ns.response(401, "Credenciales inválidas")
    def post(self):
        """Iniciar sesión de un usuario"""
        json_data = auth_ns.payload
        try:
            data = UsuarioCreateSchema().load(json_data)
        except ValidationError as err:
            return {"errors": err.messages}, 400
        return login_user_service(data)