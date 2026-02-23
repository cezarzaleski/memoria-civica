"""Schemas Pydantic para validação de dados do domínio de Enriquecimento LLM.

Definem os DTOs (Data Transfer Objects) para criar e ler enriquecimentos,
com validação de tipos e constraints.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class EnriquecimentoCreate(BaseModel):
    """Schema para criar um enriquecimento LLM.

    Valida os dados gerados pelo LLM antes de persistir.

    Attributes:
        proposicao_id: ID da proposição enriquecida (obrigatório)
        modelo: Nome do modelo LLM utilizado (obrigatório)
        versao_prompt: Versão do prompt utilizado (obrigatório)
        headline: Título acessível (max 120 chars recomendado)
        resumo_simples: Resumo em linguagem simples
        impacto_cidadao: Lista de impactos concretos ao cidadão
        confianca: Score de confiança (0.0 a 1.0)
        tokens_input: Tokens de entrada consumidos
        tokens_output: Tokens de saída consumidos
    """

    proposicao_id: int = Field(description="ID da proposição enriquecida")
    modelo: str = Field(max_length=50, description="Nome do modelo LLM utilizado")
    versao_prompt: str = Field(max_length=10, description="Versão do prompt utilizado")
    headline: str | None = Field(None, description="Título acessível da proposição (max 120 chars recomendado)")
    resumo_simples: str | None = Field(None, description="Resumo em linguagem simples")
    impacto_cidadao: list[str] | None = Field(None, description="Lista de impactos concretos ao cidadão")
    confianca: float = Field(default=1.0, ge=0.0, le=1.0, description="Score de confiança do LLM (0.0 a 1.0)")
    tokens_input: int | None = Field(None, ge=0, description="Tokens de entrada consumidos")
    tokens_output: int | None = Field(None, ge=0, description="Tokens de saída consumidos")

    model_config = {"from_attributes": True}


class EnriquecimentoRead(BaseModel):
    """Schema para leitura de um enriquecimento LLM (resposta de API).

    Representa o enriquecimento tal como está persistido no banco.

    Attributes:
        id: Identificador único
        proposicao_id: ID da proposição enriquecida
        modelo: Nome do modelo LLM utilizado
        versao_prompt: Versão do prompt utilizado
        headline: Título acessível
        resumo_simples: Resumo em linguagem simples
        impacto_cidadao: Lista de impactos concretos ao cidadão
        confianca: Score de confiança
        necessita_revisao: Flag para revisão manual
        tokens_input: Tokens de entrada consumidos
        tokens_output: Tokens de saída consumidos
        gerado_em: Data/hora da geração
    """

    id: int
    proposicao_id: int
    modelo: str
    versao_prompt: str
    headline: str | None = None
    resumo_simples: str | None = None
    impacto_cidadao: list[str] | None = None
    confianca: float
    necessita_revisao: bool
    tokens_input: int | None = None
    tokens_output: int | None = None
    gerado_em: datetime

    model_config = {"from_attributes": True}
