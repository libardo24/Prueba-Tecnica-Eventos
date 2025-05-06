from marshmallow import Schema, fields

class EventoSchema(Schema):
    id = fields.Int()
    nombre = fields.Str()
    descripcion = fields.Str()
    fecha_inicio = fields.DateTime()
    fecha_fin = fields.DateTime()
    capacidad_maxima = fields.Int()
    estado = fields.Str()

class EventoCreateSchema(Schema):
    nombre = fields.Str(required=True)
    descripcion = fields.Str()
    fecha_inicio = fields.DateTime(required=True)
    fecha_fin = fields.DateTime(required=True)
    capacidad_maxima = fields.Int(required=True)
    estado = fields.Str(load_default="activo")


