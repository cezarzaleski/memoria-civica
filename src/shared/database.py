"""Gerenciamento de banco de dados SQLAlchemy.

Este módulo fornece a infraestrutura de banco de dados compartilhada por todos
os domínios: engine SQLAlchemy, SessionLocal factory e context manager get_db()
para garantir cleanup adequado de sessões.
"""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from .config import settings

# Engine SQLAlchemy configurado com check_same_thread=False para SQLite
# Este parâmetro é necessário para permitir uso de sessões em múltiplas threads
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
    echo=settings.LOG_LEVEL == "DEBUG",  # Log SQL queries em modo DEBUG
)

# Factory para criar sessões do banco de dados
# autocommit=False: transações explícitas (melhor controle)
# autoflush=False: flush manual (evita queries inesperadas)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa para models SQLAlchemy (será usado nos domínios)
Base = declarative_base()


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Context manager que fornece uma sessão do banco de dados.

    Garante que a sessão seja sempre fechada, mesmo em caso de exceção.
    Uso típico:

        with get_db() as db:
            db.query(Model).all()

    Yields:
        Session: Sessão SQLAlchemy configurada e pronta para uso.

    Examples:
        >>> with get_db() as db:
        ...     deputados = db.query(Deputado).all()
        ...     print(len(deputados))
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
