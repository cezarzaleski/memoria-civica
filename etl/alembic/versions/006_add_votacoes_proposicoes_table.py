"""add_votacoes_proposicoes_table

Revision ID: 006
Revises: 005
Create Date: 2026-02-12 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "006"
down_revision: str | Sequence[str] | None = "005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema - criar tabela votacoes_proposicoes (junction table N:N)."""
    op.create_table(
        "votacoes_proposicoes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("votacao_id", sa.Integer(), nullable=False),
        sa.Column("votacao_id_original", sa.String(50), nullable=True),
        sa.Column("proposicao_id", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.String(255), nullable=True),
        sa.Column("ementa", sa.Text(), nullable=True),
        sa.Column("sigla_tipo", sa.String(20), nullable=True),
        sa.Column("numero", sa.Integer(), nullable=True),
        sa.Column("ano", sa.Integer(), nullable=True),
        sa.Column("eh_principal", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["votacao_id"], ["votacoes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["proposicao_id"], ["proposicoes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("votacao_id", "proposicao_id", name="uq_vp_votacao_proposicao"),
    )
    op.create_index("ix_vp_votacao_id", "votacoes_proposicoes", ["votacao_id"], unique=False)
    op.create_index("ix_vp_proposicao_id", "votacoes_proposicoes", ["proposicao_id"], unique=False)
    op.create_index("ix_vp_principal", "votacoes_proposicoes", ["eh_principal"], unique=False)


def downgrade() -> None:
    """Downgrade schema - remover tabela votacoes_proposicoes."""
    op.drop_index("ix_vp_principal", table_name="votacoes_proposicoes")
    op.drop_index("ix_vp_proposicao_id", table_name="votacoes_proposicoes")
    op.drop_index("ix_vp_votacao_id", table_name="votacoes_proposicoes")
    op.drop_table("votacoes_proposicoes")
