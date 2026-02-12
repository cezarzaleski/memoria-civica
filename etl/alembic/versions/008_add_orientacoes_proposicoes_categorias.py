"""add_orientacoes_proposicoes_categorias

Revision ID: 008
Revises: 007
Create Date: 2026-02-12 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "008"
down_revision: str | Sequence[str] | None = "007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema - criar tabelas orientacoes e proposicoes_categorias."""
    # Tabela orientacoes
    op.create_table(
        "orientacoes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("votacao_id", sa.Integer(), nullable=False),
        sa.Column("votacao_id_original", sa.String(50), nullable=True),
        sa.Column("sigla_bancada", sa.String(100), nullable=False),
        sa.Column("orientacao", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["votacao_id"], ["votacoes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("votacao_id", "sigla_bancada", name="uq_orientacao_votacao_bancada"),
    )
    op.create_index("ix_orientacoes_votacao_id", "orientacoes", ["votacao_id"], unique=False)
    op.create_index("ix_orientacoes_bancada", "orientacoes", ["sigla_bancada"], unique=False)

    # Tabela proposicoes_categorias
    op.create_table(
        "proposicoes_categorias",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("proposicao_id", sa.Integer(), nullable=False),
        sa.Column("categoria_id", sa.Integer(), nullable=False),
        sa.Column("origem", sa.String(20), nullable=False, server_default="regra"),
        sa.Column("confianca", sa.Float(), server_default=sa.text("1.0"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["proposicao_id"], ["proposicoes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["categoria_id"], ["categorias_civicas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "proposicao_id", "categoria_id", "origem", name="uq_pc_proposicao_categoria_origem"
        ),
    )
    op.create_index("ix_pc_proposicao_id", "proposicoes_categorias", ["proposicao_id"], unique=False)
    op.create_index("ix_pc_categoria_id", "proposicoes_categorias", ["categoria_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema - remover tabelas proposicoes_categorias e orientacoes."""
    # Remover proposicoes_categorias primeiro (depende de categorias_civicas)
    op.drop_index("ix_pc_categoria_id", table_name="proposicoes_categorias")
    op.drop_index("ix_pc_proposicao_id", table_name="proposicoes_categorias")
    op.drop_table("proposicoes_categorias")

    # Remover orientacoes
    op.drop_index("ix_orientacoes_bancada", table_name="orientacoes")
    op.drop_index("ix_orientacoes_votacao_id", table_name="orientacoes")
    op.drop_table("orientacoes")
