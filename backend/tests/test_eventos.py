import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from app.services.eventos import (
    obtener_eventos_service,
    crear_evento_service,
    obtener_evento_service,
    actualizar_evento_service,
    eliminar_evento_service,
    buscar_eventos_service,
    registrarse_evento_service,
    validar_capacidad_evento_service,
    obtener_mis_eventos_service,
    get_evento_or_404
)
from marshmallow import ValidationError

# Fixture para datos de evento válidos
@pytest.fixture
def evento_data():
    return {
        "nombre": "Concierto de Rock",
        "descripcion": "Un concierto increíble",
        "fecha_inicio": "2025-06-01T10:00:00",
        "fecha_fin": "2025-06-01T12:00:00",
        "capacidad_maxima": 100,
        "estado": "activo"
    }

# Fixture para un evento simulado devuelto por la base de datos
@pytest.fixture
def mock_evento():
    evento = MagicMock()
    evento._mapping = {
        "id": 1,
        "nombre": "Concierto de Rock",
        "descripcion": "Un concierto increíble",
        "fecha_inicio": datetime(2025, 6, 1, 10, 0, tzinfo=timezone.utc),
        "fecha_fin": datetime(2025, 6, 1, 12, 0, tzinfo=timezone.utc),
        "capacidad_maxima": 100,
        "estado": "activo"
    }
    evento.id = 1
    evento.capacidad_maxima = 100
    return evento

# Pruebas para get_evento_or_404
def test_get_evento_or_404_success(mock_db_session, mock_evento):
    result_mock = MagicMock()
    result_mock.fetchone.return_value = mock_evento
    mock_db_session.execute.return_value = result_mock
    result = get_evento_or_404(1)
    assert result == mock_evento
    mock_db_session.execute.assert_called_once()

def test_get_evento_or_404_not_found(mock_db_session):
    result_mock = MagicMock()
    result_mock.fetchone.return_value = None
    mock_db_session.execute.return_value = result_mock
    with pytest.raises(ValueError, match="Evento no encontrado"):
        get_evento_or_404(1)

# Pruebas para obtener_eventos_service

def test_obtener_eventos_service_success(mock_db_session, mock_evento):
    # Configurar el mock para la consulta de eventos
    result_mock = MagicMock()
    evento_dict = {
        "id": 1,
        "nombre": "Concierto de Rock",
        "descripcion": "Un concierto increíble",
        "fecha_inicio": datetime(2025, 6, 1, 10, 0, tzinfo=timezone.utc),
        "fecha_fin": datetime(2025, 6, 1, 12, 0, tzinfo=timezone.utc),
        "capacidad_maxima": 100,
        "estado": "activo"
    }
    # Simular un objeto Row con atributo _mapping
    row_mock = MagicMock()
    row_mock._mapping = evento_dict
    result_mock.fetchall.return_value = [row_mock]
    
    # Configurar el mock para el conteo total
    count_mock = MagicMock()
    count_mock.scalar.return_value = 1
    
    # Simular las dos consultas (eventos y conteo)
    mock_db_session.execute.side_effect = [count_mock, result_mock]
    
    # Crear un mock para current_user
    mock_current_user = MagicMock()

    # Simular el objeto request.args
    with patch('app.services.eventos.request', new=MagicMock()) as mock_request:
        # Configurar mock_request.args como un MagicMock
        mock_request.args = MagicMock()
        # Simular el comportamiento de args.get
        mock_request.args.get.side_effect = lambda key, default, type: type({
            'nombre': '',
            'page': '1',
            'per_page': '10'
        }.get(key, default))

        # Imprimir configuración para depuración
        print("mock_db_session.execute.side_effect configurado:", mock_db_session.execute.side_effect)

        # Llamar a la función con el mock de current_user
        result, status_code = obtener_eventos_service(mock_current_user)

        # Imprimir el resultado si falla para depurar
        if status_code != 200:
            print("Error en obtener_eventos_service:", result)

    assert status_code == 200
    assert isinstance(result, dict)
    assert "eventos" in result
    assert "total" in result
    assert len(result["eventos"]) == 1
    assert result["eventos"][0]["id"] == 1
    assert result["eventos"][0]["nombre"] == "Concierto de Rock"
    assert result["total"] == 1


def test_obtener_eventos_service_empty(mock_db_session):
    # Configurar el mock para la consulta de eventos
    result_mock = MagicMock()
    result_mock.fetchall.return_value = []  # Lista vacía para simular que no hay eventos
    
    # Configurar el mock para el conteo total
    count_mock = MagicMock()
    count_mock.scalar.return_value = 0  # Conteo total de 0
    
    # Simular las dos consultas (primero conteo, luego eventos)
    mock_db_session.execute.side_effect = [count_mock, result_mock]
    
    # Crear un mock para current_user
    mock_current_user = MagicMock()

    # Simular el objeto request.args
    with patch('app.services.eventos.request', new=MagicMock()) as mock_request:
        # Configurar mock_request.args como un MagicMock
        mock_request.args = MagicMock()
        # Simular el comportamiento de args.get
        mock_request.args.get.side_effect = lambda key, default, type: type({
            'nombre': '',
            'page': '1',
            'per_page': '10'
        }.get(key, default))

        # Llamar a la función con el mock de current_user
        result, status_code = obtener_eventos_service(mock_current_user)

        # Imprimir el resultado si falla para depurar
        if status_code != 200:
            print("Error en obtener_eventos_service_empty:", result)

    assert status_code == 200
    assert isinstance(result, dict)
    assert "eventos" in result
    assert "total" in result
    assert result["eventos"] == []
    assert result["total"] == 0

# Pruebas para crear_evento_service
def test_crear_evento_service_success(mock_db_session, evento_data, mock_evento):
    result_mock = MagicMock()
    result_mock.fetchone.return_value = mock_evento
    mock_db_session.execute.return_value = result_mock
    result, status_code = crear_evento_service(evento_data)
    assert status_code == 201
    assert result["id"] == 1
    assert result["nombre"] == "Concierto de Rock"
    mock_db_session.commit.assert_called_once()

def test_crear_evento_service_validation_error(mock_db_session):
    invalid_data = {"nombre": "Evento", "capacidad_maxima": 100}  # Falta fecha_inicio y fecha_fin
    result, status_code = crear_evento_service(invalid_data)
    assert status_code == 400
    assert "errors" in result
    assert "fecha_inicio" in result["errors"]

def test_crear_evento_service_db_error(mock_db_session, evento_data):
    mock_db_session.execute.side_effect = Exception("DB Error")
    result, status_code = crear_evento_service(evento_data)
    assert status_code == 500
    assert result["message"] == "Error al crear el evento: DB Error"

# Pruebas para obtener_evento_service
def test_obtener_evento_service_success(mock_db_session, mock_evento):
    result_mock = MagicMock()
    result_mock.fetchone.return_value = mock_evento
    mock_db_session.execute.return_value = result_mock
    result, status_code = obtener_evento_service(1)
    assert status_code == 200
    assert result["id"] == 1
    assert result["nombre"] == "Concierto de Rock"

def test_obtener_evento_service_not_found(mock_db_session):
    result_mock = MagicMock()
    result_mock.fetchone.return_value = None
    mock_db_session.execute.return_value = result_mock
    result, status_code = obtener_evento_service(1)
    assert status_code == 404
    assert result["message"] == "Evento no encontrado"

def test_obtener_evento_service_db_error(mock_db_session):
    mock_db_session.execute.side_effect = Exception("DB Error")
    result, status_code = obtener_evento_service(1)
    assert status_code == 500
    assert result["message"] == "Error al obtener el evento: DB Error"

# Pruebas para actualizar_evento_service
def test_actualizar_evento_service_success(mock_db_session, evento_data):
    result_mock = MagicMock()
    result_mock.rowcount = 1
    mock_db_session.execute.return_value = result_mock
    result, status_code = actualizar_evento_service(1, evento_data)
    assert status_code == 200
    assert result["message"] == "Evento actualizado exitosamente"
    mock_db_session.commit.assert_called_once()

def test_actualizar_evento_service_not_found(mock_db_session, evento_data):
    result_mock = MagicMock()
    result_mock.rowcount = 0
    mock_db_session.execute.return_value = result_mock
    result, status_code = actualizar_evento_service(1, evento_data)
    assert status_code == 404
    assert result["message"] == "Evento no encontrado"

def test_actualizar_evento_service_validation_error(mock_db_session):
    invalid_data = {"nombre": "Evento", "capacidad_maxima": 100}  # Falta fecha_inicio y fecha_fin
    result, status_code = actualizar_evento_service(1, invalid_data)
    assert status_code == 400
    assert "errors" in result
    assert "fecha_inicio" in result["errors"]

def test_actualizar_evento_service_db_error(mock_db_session, evento_data):
    mock_db_session.execute.side_effect = Exception("DB Error")
    result, status_code = actualizar_evento_service(1, evento_data)
    assert status_code == 500
    assert result["message"] == "Error al actualizar el evento: DB Error"

# Pruebas para eliminar_evento_service
def test_eliminar_evento_service_success(mock_db_session):
    # Simular las tres consultas de eliminación
    result_mock_asistentes = MagicMock(rowcount=0)  # Eliminar asistentes
    result_mock_sesiones = MagicMock(rowcount=0)    # Eliminar sesiones
    result_mock_evento = MagicMock(rowcount=1)      # Eliminar evento
    mock_db_session.execute.side_effect = [
        result_mock_asistentes,
        result_mock_sesiones,
        result_mock_evento
    ]
    result, status_code = eliminar_evento_service(1)
    assert status_code == 204
    assert result["message"] == "Evento eliminado exitosamente"
    assert mock_db_session.execute.call_count == 3  # Eliminar asistentes, sesiones y evento

def test_eliminar_evento_service_not_found(mock_db_session):
    # Simular las tres consultas de eliminación, con rowcount=0 para evento
    result_mock_asistentes = MagicMock(rowcount=0)  # Eliminar asistentes
    result_mock_sesiones = MagicMock(rowcount=0)    # Eliminar sesiones
    result_mock_evento = MagicMock(rowcount=0)      # Eliminar evento (rowcount=0 para simular no encontrado)
    mock_db_session.execute.side_effect = [
        result_mock_asistentes,
        result_mock_sesiones,
        result_mock_evento
    ]
    result, status_code = eliminar_evento_service(1)
    assert status_code == 404
    assert result["message"] == "Evento no encontrado"

def test_eliminar_evento_service_db_error(mock_db_session):
    mock_db_session.execute.side_effect = Exception("DB Error")
    result, status_code = eliminar_evento_service(1)
    assert status_code == 500
    assert result["message"] == "Error al eliminar el evento: DB Error"

# Pruebas para buscar_eventos_service
def test_buscar_eventos_service_success(mock_db_session, mock_evento):
    result_mock = MagicMock()
    result_mock.fetchall.return_value = [mock_evento]
    mock_db_session.execute.return_value = result_mock
    result, status_code = buscar_eventos_service("Rock")
    assert status_code == 200
    assert len(result) == 1
    assert result[0]["nombre"] == "Concierto de Rock"

def test_buscar_eventos_service_no_results(mock_db_session):
    result_mock = MagicMock()
    result_mock.fetchall.return_value = []
    mock_db_session.execute.return_value = result_mock
    result, status_code = buscar_eventos_service("Jazz")
    assert status_code == 200
    assert result == []

# Pruebas para registrarse_evento_service
@pytest.fixture
def current_user():
    return {"id": 1}

def test_registrarse_evento_service_success(mock_db_session, mock_evento, current_user):
    # Simular las consultas necesarias
    result_get_evento = MagicMock()
    result_get_evento.fetchone.return_value = mock_evento  # get_evento_or_404
    result_verificar = MagicMock()
    result_verificar.fetchone.return_value = None  # Verificar registro existente
    result_count = MagicMock()
    result_count.scalar.return_value = 50  # Contar asistentes (capacidad_maxima = 100)
    result_insert = MagicMock(rowcount=1)  # Insertar registro
    mock_db_session.execute.side_effect = [
        result_get_evento,
        result_verificar,
        result_count,
        result_insert
    ]
    result, status_code = registrarse_evento_service(current_user, 1)
    assert status_code == 200
    assert result["message"] == "Te has registrado exitosamente al evento"
    mock_db_session.commit.assert_called_once()

def test_registrarse_evento_service_already_registered(mock_db_session, mock_evento, current_user):
    # Simular las consultas necesarias
    result_get_evento = MagicMock()
    result_get_evento.fetchone.return_value = mock_evento  # get_evento_or_404
    result_verificar = MagicMock()
    result_verificar.fetchone.return_value = MagicMock()  # Registro existente
    mock_db_session.execute.side_effect = [
        result_get_evento,
        result_verificar
    ]
    result, status_code = registrarse_evento_service(current_user, 1)
    assert status_code == 400
    assert result["message"] == "Ya te has registrado a este evento"

def test_registrarse_evento_service_capacity_exceeded(mock_db_session, mock_evento, current_user):
    # Simular las consultas necesarias
    result_get_evento = MagicMock()
    result_get_evento.fetchone.return_value = mock_evento  # get_evento_or_404
    result_verificar = MagicMock()
    result_verificar.fetchone.return_value = None  # Verificar registro existente
    result_count = MagicMock()
    result_count.scalar.return_value = 100  # Contar asistentes (capacidad_maxima = 100)
    mock_db_session.execute.side_effect = [
        result_get_evento,
        result_verificar,
        result_count
    ]
    result, status_code = registrarse_evento_service(current_user, 1)
    assert status_code == 400
    assert result["message"] == "El evento ha alcanzado su capacidad máxima"

def test_registrarse_evento_service_not_found(mock_db_session, current_user):
    result_mock = MagicMock()
    result_mock.fetchone.return_value = None  # get_evento_or_404
    mock_db_session.execute.return_value = result_mock
    result, status_code = registrarse_evento_service(current_user, 1)
    assert status_code == 404
    assert result["message"] == "Evento no encontrado"

def test_registrarse_evento_service_db_error(mock_db_session, mock_evento, current_user):
    # Simular las consultas necesarias
    result_get_evento = MagicMock()
    result_get_evento.fetchone.return_value = mock_evento  # get_evento_or_404
    result_verificar = MagicMock()
    result_verificar.fetchone.return_value = None  # Verificar registro existente
    mock_db_session.execute.side_effect = [
        result_get_evento,
        result_verificar,
        Exception("DB Error")  # Error al contar asistentes
    ]
    result, status_code = registrarse_evento_service(current_user, 1)
    assert status_code == 500
    assert result["message"] == "Error al registrarse al evento: DB Error"

# Pruebas para validar_capacidad_evento_service
def test_validar_capacidad_evento_service_success(mock_db_session, mock_evento):
    # Simular las consultas necesarias
    result_get_evento = MagicMock()
    result_get_evento.fetchone.return_value = mock_evento  # get_evento_or_404
    result_count = MagicMock()
    result_count.scalar.return_value = 50  # Contar asistentes
    mock_db_session.execute.side_effect = [
        result_get_evento,
        result_count
    ]
    result, status_code = validar_capacidad_evento_service(1)
    assert status_code == 200
    assert result["capacidad_disponible"] == 50  # 100 - 50

def test_validar_capacidad_evento_service_not_found(mock_db_session):
    result_mock = MagicMock()
    result_mock.fetchone.return_value = None  # get_evento_or_404
    mock_db_session.execute.return_value = result_mock
    result, status_code = validar_capacidad_evento_service(1)
    assert status_code == 404
    assert result["message"] == "Evento no encontrado"

def test_validar_capacidad_evento_service_db_error(mock_db_session, mock_evento):
    # Simular las consultas necesarias
    result_get_evento = MagicMock()
    result_get_evento.fetchone.return_value = mock_evento  # get_evento_or_404
    mock_db_session.execute.side_effect = [
        result_get_evento,
        Exception("DB Error")  # Error al contar asistentes
    ]
    result, status_code = validar_capacidad_evento_service(1)
    assert status_code == 500
    assert result["message"] == "Error al validar capacidad: DB Error"

# Pruebas para obtener_mis_eventos_service
def test_obtener_mis_eventos_service_success(mock_db_session, mock_evento, current_user):
    # Configurar el mock para la consulta de eventos
    result_mock = MagicMock()
    evento_dict = {
        "id": 1,
        "nombre": "Concierto de Rock",
        "descripcion": "Un concierto increíble",
        "fecha_inicio": datetime(2025, 6, 1, 10, 0, tzinfo=timezone.utc),
        "fecha_fin": datetime(2025, 6, 1, 12, 0, tzinfo=timezone.utc),
        "capacidad_maxima": 100,
        "estado": "activo"
    }
    # Simular un objeto Row con atributo _mapping
    row_mock = MagicMock()
    row_mock._mapping = evento_dict
    result_mock.fetchall.return_value = [row_mock]
    
    # Configurar el mock para el conteo total
    count_mock = MagicMock()
    count_mock.scalar.return_value = 1
    
    # Simular las dos consultas (primero conteo, luego eventos)
    mock_db_session.execute.side_effect = [count_mock, result_mock]
    
    # Simular el objeto request.args
    with patch('app.services.eventos.request', new=MagicMock()) as mock_request:
        # Configurar mock_request.args como un MagicMock
        mock_request.args = MagicMock()
        # Simular el comportamiento de args.get
        mock_request.args.get.side_effect = lambda key, default, type: type({
            'page': '1',
            'per_page': '10'
        }.get(key, default))

        # Llamar a la función con solo current_user
        result, status_code = obtener_mis_eventos_service(current_user)

        # Imprimir el resultado si falla para depurar
        if status_code != 200:
            print("Error en obtener_mis_eventos_service:", result)
    
    assert status_code == 200
    assert result['total'] == 1
    assert len(result['eventos']) == 1
    assert result['eventos'][0]['id'] == 1

def test_obtener_mis_eventos_service_no_events(mock_db_session, current_user):
    # Configurar el mock para la consulta de eventos
    result_mock = MagicMock()
    result_mock.fetchall.return_value = []  # Lista vacía para simular que no hay eventos
    
    # Configurar el mock para el conteo total
    count_mock = MagicMock()
    count_mock.scalar.return_value = 0  # Conteo total de 0
    
    # Simular las dos consultas (primero conteo, luego eventos)
    mock_db_session.execute.side_effect = [count_mock, result_mock]
    
    # Simular el objeto request.args
    with patch('app.services.eventos.request', new=MagicMock()) as mock_request:
        # Configurar mock_request.args como un MagicMock
        mock_request.args = MagicMock()
        # Simular el comportamiento de args.get
        mock_request.args.get.side_effect = lambda key, default, type: type({
            'page': '1',
            'per_page': '10'
        }.get(key, default))

        # Llamar a la función con solo current_user
        result, status_code = obtener_mis_eventos_service(current_user)

        # Imprimir el resultado si falla para depurar
        if status_code != 200:
            print("Error en obtener_mis_eventos_service_no_events:", result)
    
    assert status_code == 200
    assert result['total'] == 0
    assert result['eventos'] == []