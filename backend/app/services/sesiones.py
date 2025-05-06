from sqlalchemy import insert, select, update, delete, func, and_
from app.models.eventos import eventos_table
from app.models.sesiones import sesiones_table
from app.models.associations import asistentes_sesion, asistentes_evento
from app.schemas.sesiones import SesionCreateSchema, SesionSchema
from app.models.usuarios import usuarios_table
from app import db
from marshmallow import ValidationError

def crear_sesion_service(json_data):
    try:
        data = SesionCreateSchema().load(json_data)
    except ValidationError as err:
        return {"errors": err.messages}, 400

    # Obtener evento
    stmt_evento = select(eventos_table).where(eventos_table.c.id == data['evento_id'])
    evento = db.session.execute(stmt_evento).fetchone()
    if not evento:
        return {"message": "Evento no encontrado"}, 404

    evento_data = dict(evento._mapping)

    # Convertir a naive datetime (sin zona horaria)
    evento_inicio = evento_data['fecha_inicio'].replace(tzinfo=None)
    evento_fin = evento_data['fecha_fin'].replace(tzinfo=None)
    sesion_inicio = data['fecha_inicio'].replace(tzinfo=None)
    sesion_fin = data['fecha_fin'].replace(tzinfo=None)

    # Validar que la sesión esté dentro del rango del evento
    if not (evento_inicio <= sesion_inicio and sesion_fin <= evento_fin):
        return {"message": "Las fechas de la sesión deben estar dentro del horario del evento"}, 400

    # Verificar solapamientos con otras sesiones
    stmt_sesiones = select(sesiones_table).where(sesiones_table.c.evento_id == data['evento_id'])
    sesiones = db.session.execute(stmt_sesiones).fetchall()
    for sesion in sesiones:
        sesion_data = dict(sesion._mapping)
        sesion_existente_inicio = sesion_data['fecha_inicio'].replace(tzinfo=None)
        sesion_existente_fin = sesion_data['fecha_fin'].replace(tzinfo=None)

        if not (sesion_fin <= sesion_existente_inicio or sesion_inicio >= sesion_existente_fin):
            return {"message": "La sesión se solapa con otra sesión del evento"}, 400

    # Insertar la sesión
    stmt_insert = insert(sesiones_table).values(**data)
    db.session.execute(stmt_insert)
    db.session.commit()

    return {"message": "Sesión creada exitosamente"}, 201

def actualizar_sesion_service(id, json_data):
    try:
        data = SesionCreateSchema().load(json_data)
    except ValidationError as err:
        return {"errors": err.messages}, 400

    stmt_sesion = select(sesiones_table).where(sesiones_table.c.id == id)
    sesion = db.session.execute(stmt_sesion).fetchone()
    if not sesion:
        return {"message": "Sesión no encontrada"}, 404

    stmt_update = update(sesiones_table).where(sesiones_table.c.id == id).values(**data)
    db.session.execute(stmt_update)
    db.session.commit()

    return {"message": "Sesión actualizada exitosamente"}, 200

def eliminar_sesion_service(id):
    stmt_sesion = select(sesiones_table).where(sesiones_table.c.id == id)
    sesion = db.session.execute(stmt_sesion).fetchone()
    if not sesion:
        return {"message": "Sesión no encontrada"}, 404

    stmt_delete = delete(sesiones_table).where(sesiones_table.c.id == id)
    db.session.execute(stmt_delete)
    db.session.commit()

    return {"message": "Sesión eliminada exitosamente"}, 204

def validar_capacidad_sesion_service(id):
    stmt_sesion = select(sesiones_table).where(sesiones_table.c.id == id)
    sesion = db.session.execute(stmt_sesion).fetchone()
    if not sesion:
        return {"message": "Sesión no encontrada"}, 404

    stmt_asistentes = select(func.count()).select_from(asistentes_sesion).where(asistentes_sesion.c.sesion_id == id)
    asistentes_count = db.session.execute(stmt_asistentes).scalar()
    capacidad_disponible = sesion.capacidad_maxima - asistentes_count

    return {"capacidad_disponible": capacidad_disponible}, 200

def registrar_asistente_service(sesion_id, json_data):
    usuario_id = json_data.get('usuario_id')

    stmt_sesion = select(sesiones_table).where(sesiones_table.c.id == sesion_id)
    sesion = db.session.execute(stmt_sesion).fetchone()
    if not sesion:
        return {"message": "Sesión no encontrada"}, 404

    evento_id = sesion._mapping['evento_id']
    stmt_evento = select(asistentes_evento).where(
        (asistentes_evento.c.usuario_id == usuario_id) &
        (asistentes_evento.c.evento_id == evento_id)
    )
    registro_evento = db.session.execute(stmt_evento).fetchone()
    if not registro_evento:
        return {"message": "El usuario no está registrado en el evento"}, 400

    stmt_asistentes = select(func.count()).select_from(asistentes_sesion).where(asistentes_sesion.c.sesion_id == sesion_id)
    asistentes_count = db.session.execute(stmt_asistentes).scalar()
    if asistentes_count >= sesion._mapping['capacidad_maxima']:
        return {"message": "La sesión ha alcanzado su capacidad máxima"}, 400

    stmt_verificar = select(asistentes_sesion).where(
        (asistentes_sesion.c.usuario_id == usuario_id) &
        (asistentes_sesion.c.sesion_id == sesion_id)
    )
    registro_existente = db.session.execute(stmt_verificar).fetchone()
    if registro_existente:
        return {"message": "El usuario ya está registrado en esta sesión"}, 400

    fecha_inicio = sesion._mapping['fecha_inicio']
    fecha_fin = sesion._mapping['fecha_fin']
    stmt_conflicto = (
        select(sesiones_table.c.id)
        .select_from(sesiones_table.join(asistentes_sesion, sesiones_table.c.id == asistentes_sesion.c.sesion_id))
        .where(
            (asistentes_sesion.c.usuario_id == usuario_id) &
            and_(
                sesiones_table.c.fecha_inicio > fecha_fin,
                sesiones_table.c.fecha_fin > fecha_inicio
            )
        )
    )
    conflicto = db.session.execute(stmt_conflicto).fetchone()
    if conflicto:
        return {"message": "El usuario ya está registrado en otra sesión que se solapa con esta"}, 400

    stmt_insert = insert(asistentes_sesion).values(usuario_id=usuario_id, sesion_id=sesion_id)
    db.session.execute(stmt_insert)
    db.session.commit()

    return {"message": "Usuario registrado exitosamente en la sesión"}, 201


def listar_sesiones_service():
    sesiones_data = []
    # Obtener todas las sesiones
    stmt_sesiones = select(sesiones_table)
    sesiones = db.session.execute(stmt_sesiones).fetchall()
    for sesion in sesiones:
        sesion_id = sesion.id
        # Contar asistentes registrados en la sesión
        stmt_asistentes = select(func.count()).where(asistentes_sesion.c.sesion_id == sesion_id)
        asistentes_count = db.session.execute(stmt_asistentes).scalar()

        capacidad_disponible = sesion.capacidad_maxima - asistentes_count

        sesiones_data.append({
            "id": sesion.id,
            "evento_id": sesion.evento_id,
            "nombre": sesion.nombre,
            "descripcion": sesion.descripcion,
            "fecha_inicio": sesion.fecha_inicio.isoformat(),
            "fecha_fin": sesion.fecha_fin.isoformat(),
            "capacidad_maxima": sesion.capacidad_maxima,
            "asistentes_actuales": asistentes_count,
            "capacidad_disponible": capacidad_disponible,
            "ponente": sesion.ponente
        })

    return {"sesiones": sesiones_data}, 200


def listar_asistencias_service():
    stmt = (
        select(
            usuarios_table.c.id.label("usuario_id"),
            usuarios_table.c.email,
            sesiones_table.c.id.label("sesion_id"),
            sesiones_table.c.nombre.label("nombre_sesion"),
            sesiones_table.c.fecha_inicio
        )
        .select_from(
            asistentes_sesion
            .join(usuarios_table, asistentes_sesion.c.usuario_id == usuarios_table.c.id)
            .join(sesiones_table, asistentes_sesion.c.sesion_id == sesiones_table.c.id)
        )
    )
    resultados = db.session.execute(stmt).fetchall()
    asistencias = []
    for row in resultados:
        asistencias.append({
            "usuario_id": row.usuario_id,
            "email": row.email,
            "sesion_id": row.sesion_id,
            "nombre_sesion": row.nombre_sesion,
            "fecha_inicio": row.fecha_inicio.isoformat(),
        })
    return {"asistencias": asistencias}, 200


def asignar_ponente_service(sesion_id, data):
    ponente = data.get("ponente")
    if not ponente:
        return {"message": "El campo 'ponente' es requerido"}, 400
    stmt = (
        update(sesiones_table)
        .where(sesiones_table.c.id == sesion_id)
        .values(ponente=ponente)
    )
    result = db.session.execute(stmt)
    db.session.commit()
    if result.rowcount == 0:
        return {"message": "Sesión no encontrada"}, 404
    return {"message": f"Ponente asignado a la sesión {sesion_id}"}, 200


def obtener_sesiones_evento_service(evento_id):
    stmt = select(sesiones_table).where(sesiones_table.c.evento_id == evento_id)
    sesiones = db.session.execute(stmt).fetchall()
    return SesionSchema(many=True).dump([dict(s._mapping) for s in sesiones]), 200