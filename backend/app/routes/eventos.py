from flask_restx import Namespace, Resource, fields
from flask import request
from app.services.eventos import (
    obtener_eventos_service,
    crear_evento_service,
    obtener_evento_service,
    actualizar_evento_service,
    eliminar_evento_service,
    buscar_eventos_service,
    registrarse_evento_service,
    validar_capacidad_evento_service,
    obtener_mis_eventos_service,eliminar_registro_evento_service
)
from app.core.auth import token_required

# Crear un namespace para las rutas de eventos
evento_ns = Namespace(
    "eventos",
    description="Operaciones relacionadas con los eventos",
    security="Bearer Auth"  # Define el esquema de seguridad
)

# Agregar el esquema de seguridad a la documentación
evento_ns.authorizations = {
    "Bearer Auth": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": "Token de autenticación en formato 'Bearer <token>'"
    }
}

# Modelo de entrada para crear o actualizar un evento
evento_model = evento_ns.model("Evento", {
    "nombre": fields.String(required=True, description="Nombre del evento"),
    "descripcion": fields.String(required=True, description="Descripción del evento"),
    "fecha_inicio": fields.String(required=True, description="Fecha de inicio del evento (YYYY-MM-DD HH:MM:SS)"),
    "fecha_fin": fields.String(required=True, description="Fecha de fin del evento (YYYY-MM-DD HH:MM:SS)"),
    "capacidad_maxima": fields.Integer(required=True, description="Capacidad máxima del evento"),
    "estado": fields.String(description="Estado del evento (activo/inactivo)", default="activo")
})


@evento_ns.route("/eventos")
class ObtenerEventos(Resource):
    @evento_ns.doc(security="Bearer Auth")
    @evento_ns.expect(
        evento_ns.parser()
            .add_argument('nombre', type=str, default='', help='Nombre del evento para filtrar')
            .add_argument('page', type=int, default=1, help='Número de página')
            .add_argument('per_page', type=int, default=10, help='Eventos por página')
    )
    @evento_ns.response(200, "Lista de eventos obtenida exitosamente")
    @evento_ns.response(500, "Error interno del servidor")
    @token_required
    def get(self, current_user):
        """Obtener la lista de eventos con filtro opcional por nombre"""
        response, status_code = obtener_eventos_service(current_user)
        return response, status_code


@evento_ns.route("/crear")
class CrearEvento(Resource):
    @evento_ns.doc(security="Bearer Auth")
    @token_required
    @evento_ns.expect(evento_model)
    @evento_ns.response(201, "Evento creado exitosamente")
    @evento_ns.response(400, "Datos inválidos")
    @evento_ns.response(500, "Error interno del servidor")
    def post(self, current_user):
        """Crear un nuevo evento"""
        json_data = request.get_json()
        response, status_code = crear_evento_service(json_data)
        return response, status_code


@evento_ns.route("/<int:id>")
class ObtenerEvento(Resource):
    @evento_ns.doc(security="Bearer Auth")
    @token_required
    @evento_ns.response(200, "Evento obtenido exitosamente")
    @evento_ns.response(404, "Evento no encontrado")
    def get(self, current_user, id):
        """Obtener un evento por ID"""
        response, status_code = obtener_evento_service(id)
        return response, status_code


@evento_ns.route("/<int:id>/actualizar")
class ActualizarEvento(Resource):
    @evento_ns.doc(security="Bearer Auth")
    @token_required
    @evento_ns.expect(evento_model)
    @evento_ns.response(200, "Evento actualizado exitosamente")
    @evento_ns.response(404, "Evento no encontrado")
    @evento_ns.response(400, "Datos inválidos")
    @evento_ns.response(500, "Error interno del servidor")
    def put(self, current_user, id):
        """Actualizar un evento por ID"""
        json_data = request.get_json()
        response, status_code = actualizar_evento_service(id, json_data)
        return response, status_code


@evento_ns.route("/<int:id>/eliminar")
class EliminarEvento(Resource):
    @evento_ns.doc(security="Bearer Auth")
    @token_required
    @evento_ns.response(200, "Evento eliminado exitosamente")
    @evento_ns.response(404, "Evento no encontrado")
    def delete(self, current_user, id):
        """Eliminar un evento por ID"""
        response, status_code = eliminar_evento_service(id)
        return response, status_code


@evento_ns.route("/buscar")
class BuscarEventos(Resource):
    @evento_ns.doc(security="Bearer Auth")
    @evento_ns.param("nombre", "Nombre del evento a buscar", type="string", required=False)
    @token_required
    @evento_ns.response(200, "Eventos encontrados exitosamente")
    def get(self, current_user):
        """Buscar eventos por nombre"""
        nombre = request.args.get("nombre", "")
        response, status_code = buscar_eventos_service(nombre)
        return response, status_code


@evento_ns.route("/<int:id>/registrarse")
class RegistrarseEvento(Resource):
    @evento_ns.doc(security="Bearer Auth")
    @token_required
    @evento_ns.response(200, "Usuario registrado en el evento exitosamente")
    @evento_ns.response(404, "Evento no encontrado")
    @evento_ns.response(400, "El usuario ya está registrado o el evento está lleno")
    def post(self, current_user, id):
        """Registrar un usuario en un evento"""
        response, status_code = registrarse_evento_service(current_user, id)
        return response, status_code
@evento_ns.route("/<int:id>/eliminar-registro")
class EliminarRegistroEvento(Resource):
    @evento_ns.doc(security="Bearer Auth")
    @token_required
    @evento_ns.response(200, "Registro eliminado exitosamente")
    @evento_ns.response(404, "Evento no encontrado")
    @evento_ns.response(400, "No estás registrado en este evento")
    def delete(self, current_user, id):
        """Eliminar el registro de un usuario en un evento"""
        response, status_code = eliminar_registro_evento_service(current_user, id)
        return response, status_code

@evento_ns.route("/<int:id>/validar-capacidad")
class ValidarCapacidadEvento(Resource):
    @evento_ns.doc(security="Bearer Auth")
    @token_required
    @evento_ns.response(200, "Capacidad del evento validada exitosamente")
    @evento_ns.response(404, "Evento no encontrado")
    def get(self, current_user, id):
        """Validar la capacidad de un evento"""
        response, status_code = validar_capacidad_evento_service(id)
        return response, status_code


@evento_ns.route("/mis-eventos")
class MisEventos(Resource):
    @evento_ns.doc(security="Bearer Auth")
    @token_required
    @evento_ns.response(200, "Lista de mis eventos obtenida exitosamente")
    @evento_ns.expect(
        evento_ns.parser()
            .add_argument('page', type=int, default=1, help='Número de página')
            .add_argument('per_page', type=int, default=10, help='Eventos por página')
    )
    def get(self, current_user):
        """Obtener los eventos en los que el usuario está registrado"""
        response, status_code = obtener_mis_eventos_service(current_user)
        return response, status_code