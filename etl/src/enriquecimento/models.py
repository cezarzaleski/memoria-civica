"""Models SQLAlchemy para o domínio de Enriquecimento LLM.

Define a tabela enriquecimentos_llm com campos para armazenar
o resultado do enriquecimento de proposições legislativas via LLM.
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint

from src.shared.database import Base


class EnriquecimentoLLM(Base):
    """Model SQLAlchemy para representar um enriquecimento LLM de proposição.

    Armazena o resultado do processamento de uma ementa legislativa por LLM,
    incluindo headline acessível, resumo simplificado, lista de impactos ao
    cidadão e metadados de geração (modelo, versão do prompt, tokens).

    Attributes:
        id: Identificador único do enriquecimento (chave primária)
        proposicao_id: ID da proposição enriquecida (FK para proposicoes.id)
        modelo: Nome do modelo LLM utilizado (ex: gpt-4o-mini)
        versao_prompt: Versão do prompt utilizado (ex: v1.0)
        headline: Título acessível da proposição (max 120 chars recomendado)
        resumo_simples: Resumo em linguagem simples (~200 palavras)
        impacto_cidadao: JSON array com impactos concretos ao cidadão
        confianca: Score de confiança do LLM (0.0 a 1.0)
        necessita_revisao: Flag para revisão manual (True se confianca < 0.5)
        tokens_input: Quantidade de tokens de entrada consumidos
        tokens_output: Quantidade de tokens de saída consumidos
        gerado_em: Data/hora da geração do enriquecimento
    """

    __tablename__ = "enriquecimentos_llm"

    id = Column(Integer, primary_key=True, autoincrement=True)
    proposicao_id = Column(
        Integer,
        ForeignKey("proposicoes.id", ondelete="CASCADE"),
        nullable=False,
    )
    modelo = Column(String(50), nullable=False)
    versao_prompt = Column(String(10), nullable=False)
    headline = Column(Text, nullable=True)
    resumo_simples = Column(Text, nullable=True)
    impacto_cidadao = Column(Text, nullable=True)  # JSON array de strings
    confianca = Column(Float, nullable=False, default=1.0)
    necessita_revisao = Column(Boolean, nullable=False, default=False)
    tokens_input = Column(Integer, nullable=True)
    tokens_output = Column(Integer, nullable=True)
    gerado_em = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("proposicao_id", "versao_prompt", name="uq_enriquecimento"),
        Index("ix_enriquecimentos_proposicao", "proposicao_id"),
        Index("ix_enriquecimentos_confianca", "confianca"),
        Index("ix_enriquecimentos_revisao", "necessita_revisao"),
    )

    def __repr__(self) -> str:
        """Representação string do modelo."""
        return (
            f"<EnriquecimentoLLM(id={self.id}, proposicao_id={self.proposicao_id}, "
            f"modelo='{self.modelo}', versao_prompt='{self.versao_prompt}', "
            f"confianca={self.confianca})>"
        )
