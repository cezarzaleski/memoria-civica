"""Schemas Pydantic para validação de dados do domínio de Votações.

Definem os DTOs (Data Transfer Objects) para criar e ler votações, votos,
vínculos votação-proposição e orientações de bancada.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class VotacaoCreate(BaseModel):
    """Schema para criar uma votação.

    Valida os dados que vêm do CSV ou da API antes de persistir.

    Attributes:
        id: Identificador único (obrigatório do CSV)
        proposicao_id: ID da proposição votada (opcional, nullable)
        data_hora: Data e hora da votação (ISO 8601)
        resultado: Resultado da votação (ex: APROVADO, REJEITADO)
        eh_nominal: Se a votação é nominal
        votos_sim: Contagem de votos "Sim"
        votos_nao: Contagem de votos "Não"
        votos_outros: Contagem de outros votos
        descricao: Descrição textual da votação
        sigla_orgao: Sigla do órgão
    """

    id: int
    proposicao_id: int | None = Field(default=None, description="ID da proposição votada (opcional)")
    data_hora: datetime = Field(description="Data e hora da votação (ISO 8601)")
    resultado: str = Field(max_length=20, description="Resultado da votação (ex: APROVADO, REJEITADO)")
    eh_nominal: bool = Field(default=False, description="Se a votação é nominal")
    votos_sim: int = Field(default=0, ge=0, description="Contagem de votos Sim")
    votos_nao: int = Field(default=0, ge=0, description="Contagem de votos Não")
    votos_outros: int = Field(default=0, ge=0, description="Contagem de outros votos")
    descricao: str | None = Field(default=None, description="Descrição textual da votação")
    sigla_orgao: str | None = Field(default=None, max_length=50, description="Sigla do órgão")

    model_config = {"from_attributes": True}


class VotacaoRead(BaseModel):
    """Schema para leitura de uma votação (resposta de API).

    Representa a votação tal como está persistida no banco.
    """

    id: int
    proposicao_id: int | None
    data_hora: datetime
    resultado: str
    eh_nominal: bool
    votos_sim: int
    votos_nao: int
    votos_outros: int
    descricao: str | None
    sigla_orgao: str | None

    model_config = {"from_attributes": True}


class VotoCreate(BaseModel):
    """Schema para criar um voto.

    Valida os dados que vêm do CSV ou da API antes de persistir.
    """

    id: int
    votacao_id: int = Field(ge=1, description="ID da votação")
    deputado_id: int = Field(ge=1, description="ID do deputado")
    voto: str = Field(max_length=20, description="Tipo de voto (ex: SIM, NAO, ABSTENCAO, OBSTRUCAO)")

    model_config = {"from_attributes": True}


class VotoRead(BaseModel):
    """Schema para leitura de um voto (resposta de API).

    Representa o voto tal como está persistido no banco.
    """

    id: int
    votacao_id: int
    deputado_id: int
    voto: str

    model_config = {"from_attributes": True}


class VotacaoProposicaoCreate(BaseModel):
    """Schema para criar um vínculo votação-proposição.

    Registra a relação N:N entre votações e proposições.
    """

    votacao_id: int
    votacao_id_original: str | None = None
    proposicao_id: int
    titulo: str | None = None
    ementa: str | None = None
    sigla_tipo: str | None = None
    numero: int | None = None
    ano: int | None = None
    eh_principal: bool = False

    model_config = {"from_attributes": True}


class OrientacaoCreate(BaseModel):
    """Schema para criar uma orientação de bancada.

    Registra como uma bancada orientou seus membros em uma votação.
    """

    votacao_id: int
    votacao_id_original: str | None = None
    sigla_bancada: str
    orientacao: str

    model_config = {"from_attributes": True}
