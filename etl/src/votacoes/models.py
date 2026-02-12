"""Models SQLAlchemy para o domínio de Votações.

Define as tabelas votacoes, votos, votacoes_proposicoes e orientacoes
com campos essenciais para persistência e relacionamentos.
"""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
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


class Votacao(Base):
    """Model SQLAlchemy para representar uma votação legislativa.

    Uma votação representa um evento no qual proposições são votadas no Plenário.
    Uma votação pode ter vários votos, um de cada deputado participante.

    Attributes:
        id: Identificador único da votação (chave primária)
        proposicao_id: ID da proposição votada (FK para proposicoes.id, nullable)
        data_hora: Data e hora da votação (ISO 8601)
        resultado: Resultado da votação (ex: APROVADO, REJEITADO)
        eh_nominal: Se a votação é nominal (votos_sim > 0)
        votos_sim: Contagem de votos "Sim"
        votos_nao: Contagem de votos "Não"
        votos_outros: Contagem de outros votos (abstenção, obstrução)
        descricao: Descrição textual da votação
        sigla_orgao: Sigla do órgão (ex: PLEN, CCJC)
        proposicao: Relacionamento com Proposicao (lazy loading)
        votos: Relacionamento com Voto (lazy loading, one-to-many)
    """

    __tablename__ = "votacoes"

    id = Column(Integer, primary_key=True, index=True)
    proposicao_id = Column(
        Integer,
        ForeignKey("proposicoes.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    data_hora = Column(DateTime, nullable=False, index=True)
    resultado = Column(String(20), nullable=False)
    eh_nominal = Column(Boolean, default=False)
    votos_sim = Column(Integer, default=0)
    votos_nao = Column(Integer, default=0)
    votos_outros = Column(Integer, default=0)
    descricao = Column(Text)
    sigla_orgao = Column(String(50))

    __table_args__ = (Index("ix_votacoes_nominal", "eh_nominal"),)

    # Relacionamentos
    proposicao = relationship("Proposicao", foreign_keys=[proposicao_id])
    votos = relationship("Voto", back_populates="votacao", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """Representação string do modelo."""
        return (
            f"<Votacao(id={self.id}, proposicao_id={self.proposicao_id}, "
            f"data_hora={self.data_hora}, resultado='{self.resultado}')>"
        )


class Voto(Base):
    """Model SQLAlchemy para representar um voto individual.

    Um voto é o registro de como um deputado votou em uma votação específica.

    Attributes:
        id: Identificador único do voto (chave primária)
        votacao_id: ID da votação em que o voto foi registrado (FK para votacoes.id, obrigatório)
        deputado_id: ID do deputado que votou (FK para deputados.id, obrigatório)
        voto: Tipo de voto (ex: SIM, NAO, ABSTENCAO, OBSTRUCAO)
        votacao: Relacionamento com Votacao (lazy loading)
        deputado: Relacionamento com Deputado (lazy loading)
    """

    __tablename__ = "votos"

    id = Column(Integer, primary_key=True, index=True)
    votacao_id = Column(
        Integer,
        ForeignKey("votacoes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    deputado_id = Column(
        Integer,
        ForeignKey("deputados.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    voto = Column(String(20), nullable=False)

    # Relacionamentos
    votacao = relationship("Votacao", back_populates="votos", foreign_keys=[votacao_id])
    deputado = relationship("Deputado", foreign_keys=[deputado_id])

    def __repr__(self) -> str:
        """Representação string do modelo."""
        return (
            f"<Voto(id={self.id}, votacao_id={self.votacao_id}, "
            f"deputado_id={self.deputado_id}, voto='{self.voto}')>"
        )


class VotacaoProposicao(Base):
    """Model SQLAlchemy para a junction table votação↔proposição (N:N).

    Registra o vínculo entre uma votação e as proposições votadas,
    incluindo metadados como título, ementa e se é a proposição principal.
    """

    __tablename__ = "votacoes_proposicoes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    votacao_id = Column(Integer, ForeignKey("votacoes.id", ondelete="CASCADE"), nullable=False)
    votacao_id_original = Column(String(50))
    proposicao_id = Column(Integer, ForeignKey("proposicoes.id", ondelete="CASCADE"), nullable=False)
    titulo = Column(String(255))
    ementa = Column(Text)
    sigla_tipo = Column(String(20))
    numero = Column(Integer)
    ano = Column(Integer)
    eh_principal = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("votacao_id", "proposicao_id", name="uq_vp_votacao_proposicao"),
        Index("ix_vp_votacao_id", "votacao_id"),
        Index("ix_vp_proposicao_id", "proposicao_id"),
        Index("ix_vp_principal", "eh_principal"),
    )

    votacao = relationship("Votacao", backref=backref("votacoes_proposicoes", passive_deletes=True))
    proposicao = relationship("Proposicao", backref=backref("votacoes_proposicoes", passive_deletes=True))


class Orientacao(Base):
    """Model SQLAlchemy para orientação de bancada em uma votação.

    Registra como cada bancada/partido orientou seus membros em cada votação.
    """

    __tablename__ = "orientacoes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    votacao_id = Column(Integer, ForeignKey("votacoes.id", ondelete="CASCADE"), nullable=False)
    votacao_id_original = Column(String(50))
    sigla_bancada = Column(String(100), nullable=False)
    orientacao = Column(String(20), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("votacao_id", "sigla_bancada", name="uq_orientacao_votacao_bancada"),
        Index("ix_orientacoes_votacao_id", "votacao_id"),
        Index("ix_orientacoes_bancada", "sigla_bancada"),
    )

    votacao = relationship("Votacao", backref=backref("orientacoes", passive_deletes=True))
