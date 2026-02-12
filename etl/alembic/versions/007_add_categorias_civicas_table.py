"""add_categorias_civicas_table

Revision ID: 007
Revises: 006
Create Date: 2026-02-12 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "007"
down_revision: str | Sequence[str] | None = "006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Seed data: 9 categorias cívicas
CATEGORIAS_SEED = [
    {
        "codigo": "GASTOS_PUBLICOS",
        "nome": "Gastos Públicos",
        "descricao": "Proposições relacionadas a gastos públicos, orçamento e finanças do governo",
        "icone": "💰",
    },
    {
        "codigo": "TRIBUTACAO_AUMENTO",
        "nome": "Aumento de Tributos",
        "descricao": "Proposições que aumentam ou criam novos tributos",
        "icone": "📈",
    },
    {
        "codigo": "TRIBUTACAO_ISENCAO",
        "nome": "Isenção Tributária",
        "descricao": "Proposições que reduzem ou isentam tributos",
        "icone": "🏷️",
    },
    {
        "codigo": "BENEFICIOS_CATEGORIAS",
        "nome": "Benefícios para Categorias",
        "descricao": "Proposições que concedem benefícios a categorias profissionais específicas",
        "icone": "👔",
    },
    {
        "codigo": "DIREITOS_SOCIAIS",
        "nome": "Direitos Sociais",
        "descricao": "Proposições relacionadas a saúde, educação, moradia e direitos sociais",
        "icone": "🏥",
    },
    {
        "codigo": "SEGURANCA_JUSTICA",
        "nome": "Segurança e Justiça",
        "descricao": "Proposições relacionadas a segurança pública, sistema penal e justiça",
        "icone": "⚖️",
    },
    {
        "codigo": "MEIO_AMBIENTE",
        "nome": "Meio Ambiente",
        "descricao": "Proposições relacionadas a meio ambiente, sustentabilidade e recursos naturais",
        "icone": "🌿",
    },
    {
        "codigo": "REGULACAO_ECONOMICA",
        "nome": "Regulação Econômica",
        "descricao": "Proposições sobre regulação de mercados, empresas e atividades econômicas",
        "icone": "🏭",
    },
    {
        "codigo": "POLITICA_INSTITUCIONAL",
        "nome": "Política Institucional",
        "descricao": "Proposições sobre organização do Estado, eleições e processo legislativo",
        "icone": "🏛️",
    },
]


def upgrade() -> None:
    """Upgrade schema - criar tabela categorias_civicas e popular com 9 categorias."""
    categorias_table = op.create_table(
        "categorias_civicas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("codigo", sa.String(50), nullable=False),
        sa.Column("nome", sa.String(100), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("icone", sa.String(10), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("codigo", name="uq_categorias_civicas_codigo"),
    )

    # Seed das 9 categorias
    op.bulk_insert(categorias_table, CATEGORIAS_SEED)


def downgrade() -> None:
    """Downgrade schema - remover tabela categorias_civicas."""
    op.drop_table("categorias_civicas")
