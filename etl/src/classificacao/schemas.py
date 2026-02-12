"""Schemas Pydantic para validação de dados do domínio de Classificação Cívica.

Define o DTO para criar vínculos proposição-categoria.
"""

from pydantic import BaseModel


class ProposicaoCategoriaCreate(BaseModel):
    """Schema para criar um vínculo proposição-categoria.

    Registra a classificação de uma proposição em uma categoria cívica.
    """

    proposicao_id: int
    categoria_id: int
    origem: str = "regra"
    confianca: float = 1.0

    model_config = {"from_attributes": True}
