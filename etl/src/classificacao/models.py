"""Models SQLAlchemy para o domínio de Classificação Cívica.

Define as tabelas categorias_civicas e proposicoes_categorias para
classificação de proposições por categorias de impacto cívico.
"""

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func

from src.shared.database import Base


class CategoriaCivica(Base):
    """Model SQLAlchemy para categorias de classificação cívica.

    Tabela lookup com as categorias de impacto cívico usadas para
    classificar proposições legislativas.
    """

    __tablename__ = "categorias_civicas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(50), nullable=False, unique=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    icone = Column(String(10))


class ProposicaoCategoria(Base):
    """Model SQLAlchemy para a junction table proposição↔categoria.

    Registra a classificação de uma proposição em uma ou mais categorias
    cívicas, com origem (regra/llm) e nível de confiança.
    """

    __tablename__ = "proposicoes_categorias"

    id = Column(Integer, primary_key=True, autoincrement=True)
    proposicao_id = Column(Integer, ForeignKey("proposicoes.id", ondelete="CASCADE"), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias_civicas.id", ondelete="CASCADE"), nullable=False)
    origem = Column(String(20), nullable=False, server_default="regra")
    confianca = Column(Float, default=1.0)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("proposicao_id", "categoria_id", "origem", name="uq_pc_proposicao_categoria_origem"),
        Index("ix_pc_proposicao_id", "proposicao_id"),
        Index("ix_pc_categoria_id", "categoria_id"),
    )

    proposicao = relationship("Proposicao", backref=backref("proposicoes_categorias", passive_deletes=True))
    categoria = relationship("CategoriaCivica", backref=backref("proposicoes_categorias", passive_deletes=True))
