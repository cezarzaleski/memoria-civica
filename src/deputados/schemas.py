"""Schemas Pydantic para validação de dados do domínio de Deputados.

Definem os DTOs (Data Transfer Objects) para criar e ler deputados,
com validação de tipos e constraints.
"""


from pydantic import BaseModel, Field


class DeputadoCreate(BaseModel):
    """Schema para criar um deputado.

    Valida os dados que vêm do CSV ou da API antes de persistir.

    Attributes:
        id: Identificador único (obrigatório do CSV)
        nome: Nome completo do deputado (obrigatório, não vazio)
        partido: Sigla do partido político (obrigatório)
        uf: Unidade federativa - validação de 2 caracteres exatos
        foto_url: URL para foto (opcional)
        email: Email (opcional)

    Examples:
        >>> dep = DeputadoCreate(
        ...     id=123,
        ...     nome="João Silva",
        ...     partido="PT",
        ...     uf="SP"
        ... )
        >>> dep.uf
        'SP'
    """

    id: int
    nome: str = Field(min_length=1, max_length=255, description="Nome completo do deputado")
    partido: str = Field(min_length=1, max_length=50, description="Sigla do partido")
    uf: str = Field(
        min_length=2,
        max_length=2,
        description="Unidade federativa (estado) com exatamente 2 caracteres",
    )
    foto_url: str | None = Field(None, max_length=500, description="URL da foto")
    email: str | None = Field(None, max_length=255, description="Email de contato")

    model_config = {"from_attributes": True}


class DeputadoRead(BaseModel):
    """Schema para leitura de um deputado (resposta de API).

    Representa o deputado tal como está persistido no banco.

    Attributes:
        id: Identificador único
        nome: Nome completo
        partido: Sigla do partido
        uf: Unidade federativa
        foto_url: URL da foto
        email: Email
    """

    id: int
    nome: str
    partido: str
    uf: str
    foto_url: str | None = None
    email: str | None = None

    model_config = {"from_attributes": True}
