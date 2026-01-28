"""Alembic environment configuration.

Configuração do Alembic para migrations versionadas do banco de dados.
Suporta modo offline (gera SQL sem conexão) e online (executa diretamente no DB).
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Importar Base e settings do módulo shared
from etl.src.shared.config import settings
from etl.src.shared.database import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Configurar target_metadata com Base.metadata do shared
# Quando novos models forem criados, importá-los aqui para autogenerate funcionar:
# from etl.src.deputados.models import Deputado
# from etl.src.proposicoes.models import Proposicao
# from etl.src.votacoes.models import Votacao, Voto
target_metadata = Base.metadata

# Sobrescrever sqlalchemy.url com valor de settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # Detectar mudanças de tipo de coluna
        compare_server_default=True,  # Detectar mudanças de default
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Detectar mudanças de tipo de coluna
            compare_server_default=True,  # Detectar mudanças de default
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
