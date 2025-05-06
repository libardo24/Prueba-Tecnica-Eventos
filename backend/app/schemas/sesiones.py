from marshmallow import Schema, fields, post_load
from datetime import datetime, timezone

class SesionSchema(Schema):
    id = fields.Int()
    evento_id = fields.Int(required=True)
    nombre = fields.Str(required=True)
    descripcion = fields.Str()
    fecha_inicio = fields.DateTime(required=True)
    fecha_fin = fields.DateTime(required=True)
    capacidad_maxima = fields.Int(required=True)
    ponente = fields.Str(required=True)

class SesionCreateSchema(Schema):
    evento_id = fields.Int(required=True)
    nombre = fields.Str(required=True)
    descripcion = fields.Str()
    fecha_inicio = fields.DateTime(required=True)
    fecha_fin = fields.DateTime(required=True)
    capacidad_maxima = fields.Int(required=True)
    ponente = fields.Str(required=True)

    @post_load
    def make_timezone_aware(self, data, **kwargs):
        # Asegurarse de que las fechas sean timezone-aware (UTC)
        if "fecha_inicio" in data and data["fecha_inicio"].tzinfo is None:
            data["fecha_inicio"] = data["fecha_inicio"].replace(tzinfo=timezone.utc)
        if "fecha_fin" in data and data["fecha_fin"].tzinfo is None:
            data["fecha_fin"] = data["fecha_fin"].replace(tzinfo=timezone.utc)
        return data