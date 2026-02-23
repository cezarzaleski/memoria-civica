"""Models SQLAlchemy para o domínio de Votações.

Define as tabelas votacoes e votos com campos essenciais para persistência
e relacionamentos com Proposições e Deputados.
"""

import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.shared.database import Base


class ResultadoVotacao(enum.StrEnum):
    """Enum para os possíveis resultados de uma votação.

    Attributes:
        APROVADO: Votação foi aprovada
        REJEITADO: Votação foi rejeitada
    """

    APROVADO = "APROVADO"
    REJEITADO = "REJEITADO"


class TipoVoto(enum.StrEnum):
    """Enum para os possíveis tipos de voto.

    Attributes:
        SIM: Voto a favor
        NAO: Voto contra
        ABSTENCAO: Voto em abstenção
        OBSTRUCAO: Voto de obstrução
    """

    SIM = "SIM"
    NAO = "NAO"
    ABSTENCAO = "ABSTENCAO"
    OBSTRUCAO = "OBSTRUCAO"


class Votacao(Base):
    """Model SQLAlchemy para representar uma votação legislativa.

    Uma votação representa um evento no qual proposições são votadas no Plenário.
    Uma votação pode ter vários votos, um de cada deputado participante.

    Attributes:
        id: Identificador único da votação (chave primária)
        proposicao_id: ID da proposição votada (FK para proposicoes.id, obrigatório)
        data_hora: Data e hora da votação (ISO 8601)
        resultado: Resultado da votação (APROVADO ou REJEITADO)
        proposicao: Relacionamento com Proposicao (lazy loading)
        votos: Relacionamento com Voto (lazy loading, one-to-many)
    """

    __tablename__ = "votacoes"

    id = Column(Integer, primary_key=True, index=True)
    proposicao_id = Column(
        Integer,
        ForeignKey("proposicoes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    data_hora = Column(DateTime, nullable=False, index=True)
    resultado = Column(Enum(ResultadoVotacao), nullable=False)

    # Relacionamentos
    proposicao = relationship("Proposicao", foreign_keys=[proposicao_id])
    votos = relationship("Voto", back_populates="votacao", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """Representação string do modelo."""
        return (
            f"<Votacao(id={self.id}, proposicao_id={self.proposicao_id}, "
            f"data_hora={self.data_hora}, resultado='{self.resultado.value}')>"
        )


class Voto(Base):
    """Model SQLAlchemy para representar um voto individual.

    Um voto é o registro de como um deputado votou em uma votação específica.

    Attributes:
        id: Identificador único do voto (chave primária)
        votacao_id: ID da votação em que o voto foi registrado (FK para votacoes.id, obrigatório)
        deputado_id: ID do deputado que votou (FK para deputados.id, obrigatório)
        voto: Tipo de voto (SIM, NAO, ABSTENCAO, OBSTRUCAO)
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
    voto = Column(Enum(TipoVoto), nullable=False)

    # Relacionamentos
    votacao = relationship("Votacao", back_populates="votos", foreign_keys=[votacao_id])
    deputado = relationship("Deputado", foreign_keys=[deputado_id])

    def __repr__(self) -> str:
        """Representação string do modelo."""
        return (
            f"<Voto(id={self.id}, votacao_id={self.votacao_id}, "
            f"deputado_id={self.deputado_id}, voto='{self.voto.value}')>"
        )
