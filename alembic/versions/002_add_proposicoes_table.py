"""add_proposicoes_table

Revision ID: 002
Revises: 001
Create Date: 2026-01-23 16:30:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: str | Sequence[str] | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema - criar tabela proposicoes com FK para deputados."""
    op.create_table(
        "proposicoes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=10), nullable=False),
        sa.Column("numero", sa.Integer(), nullable=False),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("ementa", sa.Text(), nullable=False),
        sa.Column("autor_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["autor_id"], ["deputados.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_proposicoes_id", "proposicoes", ["id"], unique=False)
    op.create_index("ix_proposicoes_tipo", "proposicoes", ["tipo"], unique=False)
    op.create_index("ix_proposicoes_autor_id", "proposicoes", ["autor_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema - remover tabela proposicoes."""
    op.drop_index("ix_proposicoes_autor_id", table_name="proposicoes")
    op.drop_index("ix_proposicoes_tipo", table_name="proposicoes")
    op.drop_index("ix_proposicoes_id", table_name="proposicoes")
    op.drop_table("proposicoes")
