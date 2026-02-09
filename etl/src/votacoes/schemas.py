"""Schemas Pydantic para validação de dados do domínio de Votações.

Definem os DTOs (Data Transfer Objects) para criar e ler votações e votos,
com validação de tipos e constraints.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class VotacaoCreate(BaseModel):
    """Schema para criar uma votação.

    Valida os dados que vêm do CSV ou da API antes de persistir.

    Attributes:
        id: Identificador único (obrigatório do CSV)
        proposicao_id: ID da proposição votada (obrigatório)
        data_hora: Data e hora da votação (ISO 8601)
        resultado: Resultado da votação (ex: APROVADO, REJEITADO)

    Examples:
        >>> votacao = VotacaoCreate(
        ...     id=1,
        ...     proposicao_id=123,
        ...     data_hora="2024-01-15T14:30:00",
        ...     resultado="APROVADO"
        ... )
        >>> votacao.resultado
        'APROVADO'
    """

    id: int
    proposicao_id: int = Field(ge=1, description="ID da proposição votada")
    data_hora: datetime = Field(description="Data e hora da votação (ISO 8601)")
    resultado: str = Field(max_length=20, description="Resultado da votação (ex: APROVADO, REJEITADO)")

    model_config = {"from_attributes": True}


class VotacaoRead(BaseModel):
    """Schema para leitura de uma votação (resposta de API).

    Representa a votação tal como está persistida no banco.

    Attributes:
        id: Identificador único
        proposicao_id: ID da proposição
        data_hora: Data e hora da votação
        resultado: Resultado da votação
    """

    id: int
    proposicao_id: int
    data_hora: datetime
    resultado: str

    model_config = {"from_attributes": True}


class VotoCreate(BaseModel):
    """Schema para criar um voto.

    Valida os dados que vêm do CSV ou da API antes de persistir.

    Attributes:
        id: Identificador único (obrigatório do CSV)
        votacao_id: ID da votação (obrigatório)
        deputado_id: ID do deputado que votou (obrigatório)
        voto: Tipo de voto (ex: SIM, NAO, ABSTENCAO, OBSTRUCAO)

    Examples:
        >>> voto = VotoCreate(
        ...     id=1,
        ...     votacao_id=123,
        ...     deputado_id=456,
        ...     voto="SIM"
        ... )
        >>> voto.voto
        'SIM'
    """

    id: int
    votacao_id: int = Field(ge=1, description="ID da votação")
    deputado_id: int = Field(ge=1, description="ID do deputado")
    voto: str = Field(max_length=20, description="Tipo de voto (ex: SIM, NAO, ABSTENCAO, OBSTRUCAO)")

    model_config = {"from_attributes": True}


class VotoRead(BaseModel):
    """Schema para leitura de um voto (resposta de API).

    Representa o voto tal como está persistido no banco.

    Attributes:
        id: Identificador único
        votacao_id: ID da votação
        deputado_id: ID do deputado
        voto: Tipo de voto
    """

    id: int
    votacao_id: int
    deputado_id: int
    voto: str

    model_config = {"from_attributes": True}
