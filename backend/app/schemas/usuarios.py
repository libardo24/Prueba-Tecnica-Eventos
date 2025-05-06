from marshmallow import Schema, fields, validate

class UsuarioSchema(Schema):
    """Esquema para serializar y deserializar usuarios."""
    id = fields.Int(dump_only=True)  # Solo se incluye en la salida
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(load_only=True, required=True, validate=validate.Length(min=6, max=128))  # Solo se incluye en la entrada

class UsuarioCreateSchema(Schema):
    email = fields.Email(required=True, error_messages={"required": "El email es obligatorio"})
    password = fields.Str(
        required=True,
        validate=validate.Length(min=6, max=128, error="La contraseña debe tener entre 6 y 128 caracteres"),  # Especificar el mensaje en el validador
        error_messages={
            "required": "La contraseña es obligatoria"
        }
    )