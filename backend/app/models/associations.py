from sqlalchemy import Table, Column, Integer, ForeignKey
from app.models.shared import metadata  # Importa el metadata compartido

# Tabla de asociación para relacionar usuarios con eventos
asistentes_evento = Table(
    'asistentes_evento', metadata,
    Column('usuario_id', Integer, ForeignKey('usuarios.id', ondelete="CASCADE"), primary_key=True),
    Column('evento_id', Integer, ForeignKey('eventos.id', ondelete="CASCADE"), primary_key=True)
)

asistentes_sesion = Table(
    'asistentes_sesion', metadata,
    Column('usuario_id', Integer, ForeignKey('usuarios.id', ondelete="CASCADE"), primary_key=True),
    Column('sesion_id', Integer, ForeignKey('sesiones.id', ondelete="CASCADE"), primary_key=True)
)