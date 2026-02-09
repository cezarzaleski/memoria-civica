"""add_votacoes_table

Revision ID: 003
Revises: 002
Create Date: 2026-01-23 19:45:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: str | Sequence[str] | None = "002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema - criar tabela votacoes com FK para proposicoes."""
    op.create_table(
        "votacoes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("proposicao_id", sa.Integer(), nullable=False),
        sa.Column("data_hora", sa.DateTime(), nullable=False),
        sa.Column("resultado", sa.String(20), nullable=False),
        sa.ForeignKeyConstraint(["proposicao_id"], ["proposicoes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_votacoes_id", "votacoes", ["id"], unique=False)
    op.create_index("ix_votacoes_proposicao_id", "votacoes", ["proposicao_id"], unique=False)
    op.create_index("ix_votacoes_data_hora", "votacoes", ["data_hora"], unique=False)


def downgrade() -> None:
    """Downgrade schema - remover tabela votacoes."""
    op.drop_index("ix_votacoes_data_hora", table_name="votacoes")
    op.drop_index("ix_votacoes_proposicao_id", table_name="votacoes")
    op.drop_index("ix_votacoes_id", table_name="votacoes")
    op.drop_table("votacoes")
