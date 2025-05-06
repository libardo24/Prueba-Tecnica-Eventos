from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey
from app.models.shared import metadata  # Importa el metadata compartido
from app.models.associations import asistentes_evento  # Importa la tabla de asociación

# Definición de la tabla eventos
eventos_table = Table(
    'eventos', metadata,
    Column('id', Integer, primary_key=True),
    Column('nombre', String(100), nullable=False),
    Column('descripcion', String(500)),
    Column('fecha_inicio', DateTime, nullable=False),
    Column('fecha_fin', DateTime, nullable=False),
    Column('capacidad_maxima', Integer, nullable=False),
    Column('estado', String(50), default="activo")
)