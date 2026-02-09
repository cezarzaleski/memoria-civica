"""add_votos_table

Revision ID: 004
Revises: 003
Create Date: 2026-01-23 19:46:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: str | Sequence[str] | None = "003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema - criar tabela votos com FKs para votacoes e deputados."""
    op.create_table(
        "votos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("votacao_id", sa.Integer(), nullable=False),
        sa.Column("deputado_id", sa.Integer(), nullable=False),
        sa.Column("voto", sa.String(20), nullable=False),
        sa.ForeignKeyConstraint(["votacao_id"], ["votacoes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["deputado_id"], ["deputados.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_votos_id", "votos", ["id"], unique=False)
    op.create_index("ix_votos_votacao_id", "votos", ["votacao_id"], unique=False)
    op.create_index("ix_votos_deputado_id", "votos", ["deputado_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema - remover tabela votos."""
    op.drop_index("ix_votos_deputado_id", table_name="votos")
    op.drop_index("ix_votos_votacao_id", table_name="votos")
    op.drop_index("ix_votos_id", table_name="votos")
    op.drop_table("votos")
