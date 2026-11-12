
from logging.config import fileConfig

from alembic import context

from app.core.config import settings
from app.db.session import Base, engine
from app import models  # Import models so SQLAlchemy registers them


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Metadata used by Alembic autogenerate.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations without creating a database connection."""

    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations using the application's database engine."""

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=settings.DATABASE_URL.startswith("sqlite"),
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
