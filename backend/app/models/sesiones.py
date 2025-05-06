from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey
from app.models.shared import metadata

# Definición de la tabla sesiones
sesiones_table = Table(
    'sesiones', metadata,
    Column('id', Integer, primary_key=True),
    Column('evento_id', Integer, ForeignKey('eventos.id', ondelete="CASCADE"), nullable=False),
    Column('nombre', String(100), nullable=False),
    Column('descripcion', String(500)),
    Column('fecha_inicio', DateTime, nullable=False),
    Column('fecha_fin', DateTime, nullable=False),
    Column('capacidad_maxima', Integer, nullable=False),
    Column('ponente', String(100), nullable=False)  # Nuevo campo para el ponente
)