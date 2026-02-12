"""Schemas Pydantic para validação de dados do domínio de Proposições.

Definem os DTOs (Data Transfer Objects) para criar e ler proposições,
com validação de tipos e constraints.
"""

from enum import Enum

from pydantic import BaseModel, Field


class TipoProposicao(str, Enum):
    """Enum dos tipos válidos de proposições legislativas."""

    PL = "PL"  # Projeto de Lei
    PEC = "PEC"  # Proposta de Emenda à Constituição
    MP = "MP"  # Medida Provisória
    PLP = "PLP"  # Projeto de Lei Complementar
    PDC = "PDC"  # Projeto de Decreto Legislativo


class ProposicaoCreate(BaseModel):
    """Schema para criar uma proposição.

    Valida os dados que vêm do CSV ou da API antes de persistir.

    Attributes:
        id: Identificador único (obrigatório do CSV)
        tipo: Tipo da proposição (PL, PEC, MP, PLP, PDC)
        numero: Número sequencial da proposição
        ano: Ano de apresentação
        ementa: Descrição da proposição
        autor_id: ID do deputado autor (opcional, pode ser NULL)

    Examples:
        >>> prop = ProposicaoCreate(
        ...     id=1,
        ...     tipo="PL",
        ...     numero=123,
        ...     ano=2024,
        ...     ementa="Lei que trata de educação",
        ...     autor_id=123
        ... )
        >>> prop.tipo
        <TipoProposicao.PL: 'PL'>
    """

    id: int
    tipo: TipoProposicao = Field(description="Tipo da proposição (enum: PL, PEC, MP, PLP, PDC)")
    numero: int = Field(ge=1, description="Número da proposição")
    ano: int = Field(ge=1900, le=2100, description="Ano de apresentação")
    ementa: str = Field(min_length=1, description="Descrição da proposição")
    autor_id: int | None = Field(None, description="ID do deputado autor (opcional)")

    model_config = {"from_attributes": True}


class ProposicaoRead(BaseModel):
    """Schema para leitura de uma proposição (resposta de API).

    Representa a proposição tal como está persistida no banco.

    Attributes:
        id: Identificador único
        tipo: Tipo da proposição
        numero: Número da proposição
        ano: Ano de apresentação
        ementa: Descrição da proposição
        autor_id: ID do autor
    """

    id: int
    tipo: TipoProposicao
    numero: int
    ano: int
    ementa: str
    autor_id: int | None = None

    model_config = {"from_attributes": True}
