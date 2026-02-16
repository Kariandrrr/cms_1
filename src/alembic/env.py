import os
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.engine import Connection

from core.config import settings
from core.models import Base

load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the metadata for autogenerate
target_metadata = Base.metadata

# Получаем URL из переменной окружения или из settings
database_url = os.getenv("DATABASE_URL")
if not database_url:
    database_url = str(settings.db.url)


if "+asyncpg" in database_url:
    database_url = database_url.replace("+asyncpg", "+psycopg2")
# Для миграций используем синхронный URL
# asyncpg → psycopg2 для Alembic
if "?" in database_url:
    database_url = database_url.split("?")[0]

config.set_main_option("sqlalchemy.url", database_url)

ALEMBIC_DIR = Path(__file__).resolve().parent
FUNCTIONS_DIR = ALEMBIC_DIR / "functions"

config.set_section_option(
    "extra",
    "functions.dir",
    str(FUNCTIONS_DIR),
)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations synchronously."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Используем синхронный engine для миграций

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        # Добавляем connect_args для psycopg2
        connect_args={"connect_timeout": 30, "options": "-c statement_timeout=60000"},
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
