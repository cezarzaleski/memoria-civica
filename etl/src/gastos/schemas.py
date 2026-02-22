"""Schemas Pydantic para validação de dados do domínio de Gastos."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class GastoCreate(BaseModel):
    """Schema para criação de gastos parlamentares."""

    deputado_id: int | None = Field(default=None, ge=1, description="ID do deputado (opcional)")
    ano: int = Field(description="Ano do gasto")
    mes: int = Field(ge=1, le=12, description="Mês do gasto")
    tipo_despesa: str = Field(min_length=1, max_length=255, description="Tipo da despesa")
    tipo_documento: str | None = Field(default=None, max_length=50, description="Tipo de documento")
    data_documento: date | None = Field(default=None, description="Data do documento")
    numero_documento: str | None = Field(default=None, max_length=100, description="Número do documento")
    valor_documento: Decimal = Field(default=Decimal("0"), max_digits=12, decimal_places=2)
    valor_liquido: Decimal = Field(default=Decimal("0"), max_digits=12, decimal_places=2)
    valor_glosa: Decimal = Field(default=Decimal("0"), max_digits=12, decimal_places=2)
    nome_fornecedor: str | None = Field(default=None, max_length=255, description="Nome do fornecedor")
    cnpj_cpf_fornecedor: str | None = Field(
        default=None,
        max_length=20,
        description="CNPJ ou CPF do fornecedor",
    )
    url_documento: str | None = Field(default=None, description="URL do documento comprobatório")
    cod_documento: int | None = Field(default=None, description="Código interno do documento")
    cod_lote: int | None = Field(default=None, description="Código do lote de processamento")
    parcela: int = Field(default=0, ge=0, description="Número da parcela")

    model_config = {"from_attributes": True}


class GastoRead(GastoCreate):
    """Schema para leitura de gastos parlamentares."""

    id: int

    model_config = {"from_attributes": True}
