import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from app.services.sesiones import (
    crear_sesion_service,
    actualizar_sesion_service,
    eliminar_sesion_service,
    validar_capacidad_sesion_service,
    registrar_asistente_service,
    listar_sesiones_service,
    listar_asistencias_service,
    asignar_ponente_service
)
from marshmallow import ValidationError

# Fixture para datos de sesión válidos
@pytest.fixture
def sesion_data():
    return {
        "evento_id": 1,
        "nombre": "Taller de Python",
        "descripcion": "Un taller práctico de Python",
        "fecha_inicio": "2025-06-01T10:00:00",
        "fecha_fin": "2025-06-01T12:00:00",
        "capacidad_maxima": 50,
        "ponente": "Juan Pérez"
    }

# Fixture para un evento simulado
@pytest.fixture
def mock_evento():
    evento = MagicMock()
    evento._mapping = {
        "id": 1,
        "fecha_inicio": datetime(2025, 6, 1, 9, 0, tzinfo=timezone.utc),
        "fecha_fin": datetime(2025, 6, 1, 15, 0, tzinfo=timezone.utc)
    }
    return evento

# Fixture para una sesión simulada
@pytest.fixture
def mock_sesion():
    sesion = MagicMock()
    sesion._mapping = {
        "id": 1,
        "evento_id": 1,
        "nombre": "Taller de Python",
        "descripcion": "Un taller práctico de Python",
        "fecha_inicio": datetime(2025, 6, 1, 10, 0, tzinfo=timezone.utc),  # Rango de sesión
        "fecha_fin": datetime(2025, 6, 1, 12, 0, tzinfo=timezone.utc),      # Rango de sesión
        "capacidad_maxima": 50,
        "ponente": "Juan Pérez"
    }
    sesion.id = 1
    sesion.evento_id = 1
    sesion.capacidad_maxima = 50
    return sesion

# Pruebas para crear_sesion_service
def test_crear_sesion_service_success(mock_db_session, sesion_data, mock_evento):
    # Simulamos el evento retornado por la base de datos (lo que sería la consulta al evento)
    mock_evento_result = MagicMock()
    mock_evento_result.fetchone.return_value = mock_evento

    # Simulamos el resultado de la segunda consulta: buscar sesiones existentes
    mock_sesiones_result = MagicMock()
    mock_sesiones_result.fetchall.return_value = []  # No hay solapamiento

    # Asignamos las respuestas simuladas al side_effect
    mock_db_session.execute.side_effect = [
        mock_evento_result,    # Para buscar el evento
        mock_sesiones_result,  # Para buscar otras sesiones
        MagicMock()            # Para el insert
    ]

    # Ejecutamos la función para crear la sesión
    result, status_code = crear_sesion_service(sesion_data)

    # Verificamos que la respuesta sea la esperada
    assert status_code == 201
    assert result["message"] == "Sesión creada exitosamente"
    mock_db_session.commit.assert_called_once()

def test_crear_sesion_service_validation_error(mock_db_session):
    invalid_data = {"evento_id": 1, "nombre": "Taller"}  # Falta fecha_inicio, fecha_fin, etc.
    result, status_code = crear_sesion_service(invalid_data)
    assert status_code == 400
    assert "errors" in result
    assert "fecha_inicio" in result["errors"]

def test_crear_sesion_service_evento_not_found(mock_db_session, sesion_data):
    result_evento = MagicMock()
    result_evento.fetchone.return_value = None  # Evento no encontrado
    mock_db_session.execute.return_value = result_evento
    result, status_code = crear_sesion_service(sesion_data)
    assert status_code == 404
    assert result["message"] == "Evento no encontrado"

def test_crear_sesion_service_invalid_dates(mock_db_session, sesion_data, mock_evento):
    mock_evento._mapping["fecha_inicio"] = datetime(2025, 6, 1, 11, 0, tzinfo=timezone.utc)  # Fecha inicio del evento después de la sesión
    result_evento = MagicMock()
    result_evento.fetchone.return_value = mock_evento
    mock_db_session.execute.return_value = result_evento
    result, status_code = crear_sesion_service(sesion_data)
    assert status_code == 400
    assert result["message"] == "Las fechas de la sesión deben estar dentro del horario del evento"

def test_crear_sesion_service_overlap(mock_db_session, sesion_data, mock_evento, mock_sesion):
    result_evento = MagicMock()
    result_evento.fetchone.return_value = mock_evento
    result_sesiones = MagicMock()
    result_sesiones.fetchall.return_value = [mock_sesion]  # Sesión existente que se solapa
    mock_db_session.execute.side_effect = [
        result_evento,
        result_sesiones
    ]
    result, status_code = crear_sesion_service(sesion_data)
    assert status_code == 400
    assert result["message"] == "La sesión se solapa con otra sesión del evento"

# Pruebas para actualizar_sesion_service
def test_actualizar_sesion_service_success(mock_db_session, sesion_data, mock_sesion):
    result_sesion = MagicMock()
    result_sesion.fetchone.return_value = mock_sesion
    result_update = MagicMock()
    mock_db_session.execute.side_effect = [
        result_sesion,
        result_update
    ]
    result, status_code = actualizar_sesion_service(1, sesion_data)
    assert status_code == 200
    assert result["message"] == "Sesión actualizada exitosamente"
    mock_db_session.commit.assert_called_once()

def test_actualizar_sesion_service_not_found(mock_db_session, sesion_data):
    result_sesion = MagicMock()
    result_sesion.fetchone.return_value = None
    mock_db_session.execute.return_value = result_sesion
    result, status_code = actualizar_sesion_service(1, sesion_data)
    assert status_code == 404
    assert result["message"] == "Sesión no encontrada"

def test_actualizar_sesion_service_validation_error(mock_db_session):
    invalid_data = {"evento_id": 1, "nombre": "Taller"}  # Falta fecha_inicio, fecha_fin, etc.
    result, status_code = actualizar_sesion_service(1, invalid_data)
    assert status_code == 400
    assert "errors" in result
    assert "fecha_inicio" in result["errors"]

# Pruebas para eliminar_sesion_service
def test_eliminar_sesion_service_success(mock_db_session, mock_sesion):
    result_sesion = MagicMock()
    result_sesion.fetchone.return_value = mock_sesion
    result_delete = MagicMock()
    mock_db_session.execute.side_effect = [
        result_sesion,
        result_delete
    ]
    result, status_code = eliminar_sesion_service(1)
    assert status_code == 204
    assert result["message"] == "Sesión eliminada exitosamente"
    mock_db_session.commit.assert_called_once()

def test_eliminar_sesion_service_not_found(mock_db_session):
    result_sesion = MagicMock()
    result_sesion.fetchone.return_value = None
    mock_db_session.execute.return_value = result_sesion
    result, status_code = eliminar_sesion_service(1)
    assert status_code == 404
    assert result["message"] == "Sesión no encontrada"

# Pruebas para validar_capacidad_sesion_service
def test_validar_capacidad_sesion_service_success(mock_db_session, mock_sesion):
    result_sesion = MagicMock()
    result_sesion.fetchone.return_value = mock_sesion
    result_count = MagicMock()
    result_count.scalar.return_value = 30
    mock_db_session.execute.side_effect = [
        result_sesion,
        result_count
    ]
    result, status_code = validar_capacidad_sesion_service(1)
    assert status_code == 200
    assert result["capacidad_disponible"] == 20  # 50 - 30

def test_validar_capacidad_sesion_service_not_found(mock_db_session):
    result_sesion = MagicMock()
    result_sesion.fetchone.return_value = None
    mock_db_session.execute.return_value = result_sesion
    result, status_code = validar_capacidad_sesion_service(1)
    assert status_code == 404
    assert result["message"] == "Sesión no encontrada"

# Pruebas para registrar_asistente_service
@pytest.fixture
def asistente_data():
    return {"usuario_id": 1}

def test_registrar_asistente_service_success(mock_db_session, mock_sesion, asistente_data):
    result_sesion = MagicMock()
    result_sesion.fetchone.return_value = mock_sesion
    result_evento = MagicMock()
    result_evento.fetchone.return_value = MagicMock()  # Usuario registrado en el evento
    result_count = MagicMock()
    result_count.scalar.return_value = 20  # Asistentes actuales
    result_verificar = MagicMock()
    result_verificar.fetchone.return_value = None  # No registrado en la sesión
    result_conflicto = MagicMock()
    result_conflicto.fetchone.return_value = None  # No hay conflictos
    result_insert = MagicMock()
    mock_db_session.execute.side_effect = [
        result_sesion,
        result_evento,
        result_count,
        result_verificar,
        result_conflicto,
        result_insert
    ]
    result, status_code = registrar_asistente_service(1, asistente_data)
    assert status_code == 201
    assert result["message"] == "Usuario registrado exitosamente en la sesión"
    mock_db_session.commit.assert_called_once()

def test_registrar_asistente_service_sesion_not_found(mock_db_session, asistente_data):
    result_sesion = MagicMock()
    result_sesion.fetchone.return_value = None
    mock_db_session.execute.return_value = result_sesion
    result, status_code = registrar_asistente_service(1, asistente_data)
    assert status_code == 404
    assert result["message"] == "Sesión no encontrada"

def test_registrar_asistente_service_not_registered_event(mock_db_session, mock_sesion, asistente_data):
    result_sesion = MagicMock()
    result_sesion.fetchone.return_value = mock_sesion
    result_evento = MagicMock()
    result_evento.fetchone.return_value = None  # No registrado en el evento
    mock_db_session.execute.side_effect = [
        result_sesion,
        result_evento
    ]
    result, status_code = registrar_asistente_service(1, asistente_data)
    assert status_code == 400
    assert result["message"] == "El usuario no está registrado en el evento"

def test_registrar_asistente_service_capacity_exceeded(mock_db_session, mock_sesion, asistente_data):
    result_sesion = MagicMock()
    result_sesion.fetchone.return_value = mock_sesion
    result_evento = MagicMock()
    result_evento.fetchone.return_value = MagicMock()  # Registrado en el evento
    result_count = MagicMock()
    result_count.scalar.return_value = 50  # Capacidad máxima alcanzada
    mock_db_session.execute.side_effect = [
        result_sesion,
        result_evento,
        result_count
    ]
    result, status_code = registrar_asistente_service(1, asistente_data)
    assert status_code == 400
    assert result["message"] == "La sesión ha alcanzado su capacidad máxima"

def test_registrar_asistente_service_already_registered(mock_db_session, mock_sesion, asistente_data):
    result_sesion = MagicMock()
    result_sesion.fetchone.return_value = mock_sesion
    result_evento = MagicMock()
    result_evento.fetchone.return_value = MagicMock()  # Registrado en el evento
    result_count = MagicMock()
    result_count.scalar.return_value = 20
    result_verificar = MagicMock()
    result_verificar.fetchone.return_value = MagicMock()  # Ya registrado en la sesión
    mock_db_session.execute.side_effect = [
        result_sesion,
        result_evento,
        result_count,
        result_verificar
    ]
    result, status_code = registrar_asistente_service(1, asistente_data)
    assert status_code == 400
    assert result["message"] == "El usuario ya está registrado en esta sesión"

def test_registrar_asistente_service_conflict(mock_db_session, mock_sesion, asistente_data):
    result_sesion = MagicMock()
    result_sesion.fetchone.return_value = mock_sesion
    result_evento = MagicMock()
    result_evento.fetchone.return_value = MagicMock()  # Registrado en el evento
    result_count = MagicMock()
    result_count.scalar.return_value = 20
    result_verificar = MagicMock()
    result_verificar.fetchone.return_value = None  # No registrado en la sesión
    result_conflicto = MagicMock()
    result_conflicto.fetchone.return_value = MagicMock()  # Conflicto con otra sesión
    mock_db_session.execute.side_effect = [
        result_sesion,
        result_evento,
        result_count,
        result_verificar,
        result_conflicto
    ]
    result, status_code = registrar_asistente_service(1, asistente_data)
    assert status_code == 400
    assert result["message"] == "El usuario ya está registrado en otra sesión que se solapa con esta"

# Pruebas para listar_sesiones_service
def test_listar_sesiones_service_success(mock_db_session, mock_sesion):
    result_sesiones = MagicMock()
    result_sesiones.fetchall.return_value = [mock_sesion]
    result_count = MagicMock()
    result_count.scalar.return_value = 30
    mock_db_session.execute.side_effect = [
        result_sesiones,
        result_count
    ]
    result, status_code = listar_sesiones_service()
    assert status_code == 200
    assert len(result["sesiones"]) == 1
    assert result["sesiones"][0]["id"] == 1
    assert result["sesiones"][0]["asistentes_actuales"] == 30
    assert result["sesiones"][0]["capacidad_disponible"] == 20

def test_listar_sesiones_service_no_sesiones(mock_db_session):
    result_sesiones = MagicMock()
    result_sesiones.fetchall.return_value = []
    mock_db_session.execute.return_value = result_sesiones
    result, status_code = listar_sesiones_service()
    assert status_code == 200
    assert result["sesiones"] == []

# Pruebas para listar_asistencias_service
def test_listar_asistencias_service_success(mock_db_session):
    # Simular una fila de resultados con atributos accesibles
    row = MagicMock()
    row._mapping = {
        "usuario_id": 1,
        "email": "test@example.com",
        "sesion_id": 1,
        "nombre_sesion": "Taller de Python",
        "fecha_inicio": datetime(2025, 6, 1, 10, 0, tzinfo=timezone.utc)
    }
    # Configurar los atributos directamente para que el código pueda acceder a row.usuario_id, row.email, etc.
    row.usuario_id = 1
    row.email = "test@example.com"
    row.sesion_id = 1
    row.nombre_sesion = "Taller de Python"
    row.fecha_inicio = datetime(2025, 6, 1, 10, 0, tzinfo=timezone.utc)

    result = MagicMock()
    result.fetchall.return_value = [row]
    mock_db_session.execute.return_value = result
    result, status_code = listar_asistencias_service()
    assert status_code == 200
    assert len(result["asistencias"]) == 1
    assert result["asistencias"][0]["usuario_id"] == 1
    assert result["asistencias"][0]["email"] == "test@example.com"
    assert result["asistencias"][0]["sesion_id"] == 1
    assert result["asistencias"][0]["nombre_sesion"] == "Taller de Python"

def test_listar_asistencias_service_no_asistencias(mock_db_session):
    result = MagicMock()
    result.fetchall.return_value = []
    mock_db_session.execute.return_value = result
    result, status_code = listar_asistencias_service()
    assert status_code == 200
    assert result["asistencias"] == []

# Pruebas para asignar_ponente_service
def test_asignar_ponente_service_success(mock_db_session):
    data = {"ponente": "Ana Gómez"}
    result_update = MagicMock()
    result_update.rowcount = 1
    mock_db_session.execute.return_value = result_update
    result, status_code = asignar_ponente_service(1, data)
    assert status_code == 200
    assert result["message"] == "Ponente asignado a la sesión 1"
    mock_db_session.commit.assert_called_once()

def test_asignar_ponente_service_missing_ponente():
    data = {}
    result, status_code = asignar_ponente_service(1, data)
    assert status_code == 400
    assert result["message"] == "El campo 'ponente' es requerido"

def test_asignar_ponente_service_not_found(mock_db_session):
    data = {"ponente": "Ana Gómez"}
    result_update = MagicMock()
    result_update.rowcount = 0
    mock_db_session.execute.return_value = result_update
    result, status_code = asignar_ponente_service(1, data)
    assert status_code == 404
    assert result["message"] == "Sesión no encontrada"