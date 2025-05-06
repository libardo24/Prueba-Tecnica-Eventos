import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Añadir el path para importar desde app/
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

# Importar metadata desde tus modelos
from app.models.associations import asistentes_evento, asistentes_sesion
from app.models.eventos import eventos_table
from app.models.sesiones import sesiones_table
from app.models.usuarios import usuarios_table
from app.models.shared import metadata as target_metadata

# Obtener configuración de Alembic
config = context.config

# Sobrescribir la URL desde el .env
database_url = os.getenv("DATABASE_URL")
config.set_main_option("sqlalchemy.url", database_url)

# Configurar logging
fileConfig(config.config_file_name)

def run_migrations_offline() -> None:
    """Ejecuta migraciones en modo offline (genera SQL sin ejecutar DB)."""
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecuta migraciones en modo online (conecta a la DB)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
