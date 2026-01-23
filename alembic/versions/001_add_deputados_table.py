"""add_deputados_table

Revision ID: 001
Revises: 0b0b45871666
Create Date: 2026-01-23 16:25:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: str | Sequence[str] | None = "0b0b45871666"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema - criar tabela deputados."""
    op.create_table(
        "deputados",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("partido", sa.String(length=50), nullable=False),
        sa.Column("uf", sa.String(length=2), nullable=False),
        sa.Column("foto_url", sa.String(length=500), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_deputados_id", "deputados", ["id"], unique=False)
    op.create_index("ix_deputados_nome", "deputados", ["nome"], unique=False)
    op.create_index("ix_deputados_uf", "deputados", ["uf"], unique=False)


def downgrade() -> None:
    """Downgrade schema - remover tabela deputados."""
    op.drop_index("ix_deputados_uf", table_name="deputados")
    op.drop_index("ix_deputados_nome", table_name="deputados")
    op.drop_index("ix_deputados_id", table_name="deputados")
    op.drop_table("deputados")
