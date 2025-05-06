from sqlalchemy import select, insert, update, delete, func
from app.models.eventos import eventos_table
from app.models.associations import asistentes_evento
from app.models.sesiones import sesiones_table
from app import db
from app.schemas.eventos import EventoSchema, EventoCreateSchema
from marshmallow import ValidationError
from flask import request
from sqlalchemy.sql import func
# Utils
def serialize_result_set(result_set, schema):
    return schema.dump([dict(row._mapping) for row in result_set])

def get_evento_or_404(id):
    stmt = select(eventos_table).where(eventos_table.c.id == id)
    evento = db.session.execute(stmt).fetchone()
    if not evento:
        raise ValueError("Evento no encontrado")
    return evento

def obtener_eventos_service(current_user):
    # Obtener parámetros de paginación y filtro
    nombre = request.args.get('nombre', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    try:
        # Consulta base
        stmt = select(eventos_table)
        count_stmt = select(func.count()).select_from(eventos_table)

        # Aplicar filtro por nombre si existe
        if nombre:
            stmt = stmt.where(eventos_table.c.nombre.ilike(f"%{nombre}%"))
            count_stmt = count_stmt.where(eventos_table.c.nombre.ilike(f"%{nombre}%"))

        # Contar total de eventos
        total = db.session.execute(count_stmt).scalar()
        # Asegurarse de que total sea un entero
        total = int(total) if total is not None else 0

        # Aplicar paginación
        stmt = stmt.offset((page - 1) * per_page).limit(per_page)
        eventos = db.session.execute(stmt).fetchall()

        # Calcular total de páginas
        total_pages = (total + per_page - 1) // per_page if total > 0 else 1

        return {
            "eventos": serialize_result_set(eventos, EventoSchema(many=True)),
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }, 200
    except Exception as e:
        return {"message": f"Error al obtener eventos: {str(e)}"}, 500
def crear_evento_service(json_data):
    try:
        data = EventoCreateSchema().load(json_data)
        stmt = insert(eventos_table).values(**data).returning(eventos_table)
        evento = db.session.execute(stmt).fetchone()
        db.session.commit()
        return EventoSchema().dump(dict(evento._mapping)), 201
    except ValidationError as err:
        return {"errors": err.messages}, 400
    except Exception as e:
        return {"message": f"Error al crear el evento: {str(e)}"}, 500

def obtener_evento_service(id):
    try:
        evento = get_evento_or_404(id)
        return EventoSchema().dump(dict(evento._mapping)), 200
    except ValueError as ve:
        return {"message": str(ve)}, 404
    except Exception as e:
        return {"message": f"Error al obtener el evento: {str(e)}"}, 500

def actualizar_evento_service(id, json_data):
    try:
        data = EventoCreateSchema().load(json_data)
        stmt = update(eventos_table).where(eventos_table.c.id == id).values(**data)
        result = db.session.execute(stmt)
        if result.rowcount == 0:
            return {"message": "Evento no encontrado"}, 404
        db.session.commit()
        return {"message": "Evento actualizado exitosamente"}, 200
    except ValidationError as err:
        return {"errors": err.messages}, 400
    except Exception as e:
        return {"message": f"Error al actualizar el evento: {str(e)}"}, 500

def eliminar_evento_service(id):
    try:
        with db.session.begin():
            db.session.execute(delete(asistentes_evento).where(asistentes_evento.c.evento_id == id))
            db.session.execute(delete(sesiones_table).where(sesiones_table.c.evento_id == id))
            result = db.session.execute(delete(eventos_table).where(eventos_table.c.id == id))
            if result.rowcount == 0:
                raise ValueError("Evento no encontrado")
        return {"message": "Evento eliminado exitosamente"}, 204
    except ValueError as ve:
        return {"message": str(ve)}, 404
    except Exception as e:
        return {"message": f"Error al eliminar el evento: {str(e)}"}, 500

def buscar_eventos_service(nombre):
    stmt = select(eventos_table).where(eventos_table.c.nombre.ilike(f"%{nombre}%"))
    eventos = db.session.execute(stmt).fetchall()
    return serialize_result_set(eventos, EventoSchema(many=True)), 200

def registrarse_evento_service(current_user, id):
    try:
        evento = get_evento_or_404(id)

        stmt_verificar = select(asistentes_evento).where(
            (asistentes_evento.c.usuario_id == current_user['id']) &
            (asistentes_evento.c.evento_id == id)
        )
        registro_existente = db.session.execute(stmt_verificar).fetchone()
        if registro_existente:
            return {"message": "Ya te has registrado a este evento"}, 400

        stmt_asistentes = select(func.count()).select_from(asistentes_evento).where(
            asistentes_evento.c.evento_id == id
        )
        asistentes_count = db.session.execute(stmt_asistentes).scalar()
        if asistentes_count >= evento.capacidad_maxima:
            return {"message": "El evento ha alcanzado su capacidad máxima"}, 400

        stmt_registro = insert(asistentes_evento).values(
            usuario_id=current_user['id'], evento_id=id
        )
        db.session.execute(stmt_registro)
        db.session.commit()
        return {"message": "Te has registrado exitosamente al evento"}, 200

    except ValueError as ve:
        return {"message": str(ve)}, 404
    except Exception as e:
        return {"message": f"Error al registrarse al evento: {str(e)}"}, 500

def validar_capacidad_evento_service(id):
    try:
        evento = get_evento_or_404(id)
        stmt_asistentes = select(func.count()).select_from(asistentes_evento).where(
            asistentes_evento.c.evento_id == id
        )
        asistentes_count = db.session.execute(stmt_asistentes).scalar()
        capacidad_disponible = evento.capacidad_maxima - asistentes_count
        return {"capacidad_disponible": capacidad_disponible}, 200
    except ValueError as ve:
        return {"message": str(ve)}, 404
    except Exception as e:
        return {"message": f"Error al validar capacidad: {str(e)}"}, 500

def obtener_mis_eventos_service(current_user):
    # Obtener parámetros de paginación
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Consulta base
    stmt = (
        select(eventos_table)
        .join(asistentes_evento, asistentes_evento.c.evento_id == eventos_table.c.id)
        .where(asistentes_evento.c.usuario_id == current_user['id'])
    )

    # Contar total de eventos
    count_stmt = (
        select(func.count())
        .select_from(eventos_table)
        .join(asistentes_evento, asistentes_evento.c.evento_id == eventos_table.c.id)
        .where(asistentes_evento.c.usuario_id == current_user['id'])
    )
    total = db.session.execute(count_stmt).scalar()

    # Aplicar paginación
    eventos = db.session.execute(
        stmt.offset((page - 1) * per_page).limit(per_page)
    ).fetchall()

    return {
        "eventos": serialize_result_set(eventos, EventoSchema(many=True)),
        "total": total
    }, 200
#eliminar_registro_evento_service
def eliminar_registro_evento_service(current_user, id):
    try:
        # Verificar si el evento existe
        evento = get_evento_or_404(id)

        # Verificar si el usuario está registrado en el evento
        stmt_verificar = select(asistentes_evento).where(
            (asistentes_evento.c.usuario_id == current_user['id']) &
            (asistentes_evento.c.evento_id == id)
        )
        registro_existente = db.session.execute(stmt_verificar).fetchone()
        if not registro_existente:
            return {"message": "No estás registrado en este evento"}, 400

        # Eliminar el registro
        stmt_eliminar = delete(asistentes_evento).where(
            (asistentes_evento.c.usuario_id == current_user['id']) &
            (asistentes_evento.c.evento_id == id)
        )
        db.session.execute(stmt_eliminar)
        db.session.commit()
        return {"message": "Tu registro al evento ha sido eliminado exitosamente"}, 200

    except ValueError as ve:
        return {"message": str(ve)}, 404
    except Exception as e:
        db.session.rollback()
        return {"message": f"Error al eliminar el registro: {str(e)}"}, 500
    
def obtener_sesiones_evento_service(evento_id):
    stmt = select(sesiones_table).where(sesiones_table.c.evento_id == evento_id)
    sesiones = db.session.execute(stmt).fetchall()
    return SesionSchema(many=True).dump([dict(s._mapping) for s in sesiones]), 200