from flask_restx import Namespace, Resource, fields
from flask import request
from app.services.sesiones import (
    crear_sesion_service,
    actualizar_sesion_service,
    eliminar_sesion_service,
    validar_capacidad_sesion_service,
    registrar_asistente_service,listar_sesiones_service, listar_asistencias_service,asignar_ponente_service,obtener_sesiones_evento_service
)
from app.core.auth import token_required

sesion_ns = Namespace(
    "sesiones",
    description="Operaciones relacionadas con las sesiones",
    security="Bearer Auth"  # Define el esquema de seguridad
)

# Agregar el esquema de seguridad a la documentación
sesion_ns.authorizations = {
    "Bearer Auth": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": "Token de autenticación en formato 'Bearer <token>'"
    }
}

# Modelo de entrada para crear o actualizar una sesión
sesion_model = sesion_ns.model("Sesion", {
    "evento_id": fields.Integer(required=True, description="ID del evento al que pertenece la sesión"),
    "nombre": fields.String(required=True, description="Nombre de la sesión"),
    "descripcion": fields.String(required=True, description="Descripción de la sesión"),
    "fecha_inicio": fields.String(required=True, description="Fecha de inicio de la sesión (YYYY-MM-DD HH:MM:SS)"),
    "fecha_fin": fields.String(required=True, description="Fecha de fin de la sesión (YYYY-MM-DD HH:MM:SS)"),
    "capacidad_maxima": fields.Integer(required=True, description="Capacidad máxima de la sesión"),
    "ponente": fields.String(required=True, description="Nombre del ponente de la sesión")
})
asistencia_output_model = sesion_ns.model("AsistenciaOutput", {
    "usuario_id": fields.Integer,
    "email": fields.String,
    "sesion_id": fields.Integer,
    "nombre_sesion": fields.String,
    "fecha_inicio": fields.String
})

# Modelo de entrada para registrar un asistente
asistente_model = sesion_ns.model("Asistente", {
    "usuario_id": fields.Integer(required=True, description="ID del usuario que se registrará en la sesión")
})
ponente_model = sesion_ns.model("PonenteInput", {
    "ponente": fields.String(required=True, description="Nombre del ponente")
})

# Ruta para crear una sesión
@sesion_ns.route("/crear")
class CrearSesion(Resource):
    @sesion_ns.doc(security="Bearer Auth")
    @token_required
    @sesion_ns.expect(sesion_model)
    @sesion_ns.response(201, "Sesión creada exitosamente")
    def post(self, current_user):
        """Crear una nueva sesión"""
        json_data = request.get_json()
        return crear_sesion_service(json_data)
# Ruta para listar todas las sesiones
@sesion_ns.route("/sesiones")
class ListarSesiones(Resource):
    @sesion_ns.doc(security="Bearer Auth")
    @token_required
    @sesion_ns.response(200, "Lista de sesiones obtenida correctamente")
    def get(self, current_user): 
        """ Lista todas las sesiones disponibles con su capacidad actual y ponente.  """      
        return listar_sesiones_service()

# Ruta para actualizar una sesión
@sesion_ns.route("/actualizar/<int:id>")
class ActualizarSesion(Resource):
    @sesion_ns.doc(security="Bearer Auth")
    @token_required
    @sesion_ns.expect(sesion_model)
    @sesion_ns.response(200, "Sesión actualizada exitosamente")
    def put(self, current_user, id):
        """Actualizar una sesión por ID"""
        json_data = request.get_json()
        return actualizar_sesion_service(id, json_data)

# Ruta para eliminar una sesión
@sesion_ns.route("/eliminar/<int:id>")
class EliminarSesion(Resource):
    @sesion_ns.doc(security="Bearer Auth")
    @token_required
    @sesion_ns.response(200, "Sesión eliminada exitosamente")
    def delete(self, current_user, id):
        """Eliminar una sesión por ID"""
        return eliminar_sesion_service(id)

# Ruta para validar la capacidad de una sesión
@sesion_ns.route("/validar_capacidad/<int:id>")
class ValidarCapacidadSesion(Resource):
    @sesion_ns.doc(security="Bearer Auth")
    @token_required
    @sesion_ns.response(200, "Capacidad de la sesión validada exitosamente")
    def get(self, current_user, id):
        """Validar la capacidad de una sesión"""
        return validar_capacidad_sesion_service(id)

# Ruta para registrar un asistente en una sesión
@sesion_ns.route("/registrar_asistente/<int:sesion_id>")
class RegistrarAsistente(Resource):
    @sesion_ns.doc(security="Bearer Auth")
    @token_required
    @sesion_ns.expect(asistente_model)
    @sesion_ns.response(201, "Asistente registrado exitosamente")
    def post(self, current_user, sesion_id):
        """Registrar un asistente en una sesión"""
        json_data = request.get_json()
        return registrar_asistente_service(sesion_id, json_data)
    
@sesion_ns.route("/asistencias")
class ListarAsistencias(Resource):
    @sesion_ns.doc(security="Bearer Auth")
    @token_required
    @sesion_ns.response(200, "Lista de asistencias obtenida correctamente")
    @sesion_ns.marshal_with(sesion_ns.model("AsistenciaList", {
        "asistencias": fields.List(fields.Nested(asistencia_output_model))
    }))
    def get(self, current_user):
        """Listar todas las asistencias a sesiones"""
        return listar_asistencias_service()
    
@sesion_ns.route("/asignar_ponente/<int:sesion_id>")
class AsignarPonente(Resource):
    @sesion_ns.doc(security="Bearer Auth")
    @token_required
    @sesion_ns.expect(ponente_model)
    @sesion_ns.response(200, "Ponente asignado correctamente")
    @sesion_ns.response(404, "Sesión no encontrada")
    def put(self, current_user, sesion_id):
        """Asignar un ponente a una sesión"""
        json_data = request.get_json()
        return asignar_ponente_service(sesion_id, json_data)
    


@sesion_ns.route("/<int:evento_id>/sesiones")
class SesionesEvento(Resource):
    @sesion_ns.doc(security="Bearer Auth")
    @sesion_ns.response(200, "Lista de sesiones obtenida exitosamente")
    def get(self, evento_id):
        """Obtener las sesiones de un evento"""
        response, status_code = obtener_sesiones_evento_service(evento_id)
        return response, status_code