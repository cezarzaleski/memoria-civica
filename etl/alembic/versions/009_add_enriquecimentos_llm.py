"""add_enriquecimentos_llm

Revision ID: 009
Revises: 008
Create Date: 2026-02-23 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "009"
down_revision: str | Sequence[str] | None = "008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema - criar tabela enriquecimentos_llm."""
    op.create_table(
        "enriquecimentos_llm",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("proposicao_id", sa.Integer(), nullable=False),
        sa.Column("modelo", sa.String(50), nullable=False),
        sa.Column("versao_prompt", sa.String(10), nullable=False),
        sa.Column("headline", sa.Text(), nullable=True),
        sa.Column("resumo_simples", sa.Text(), nullable=True),
        sa.Column("impacto_cidadao", sa.Text(), nullable=True),
        sa.Column("confianca", sa.Float(), nullable=False, server_default=sa.text("1.0")),
        sa.Column("necessita_revisao", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("tokens_input", sa.Integer(), nullable=True),
        sa.Column("tokens_output", sa.Integer(), nullable=True),
        sa.Column("gerado_em", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["proposicao_id"], ["proposicoes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("proposicao_id", "versao_prompt", name="uq_enriquecimento"),
    )
    op.create_index("ix_enriquecimentos_proposicao", "enriquecimentos_llm", ["proposicao_id"], unique=False)
    op.create_index("ix_enriquecimentos_confianca", "enriquecimentos_llm", ["confianca"], unique=False)
    op.create_index("ix_enriquecimentos_revisao", "enriquecimentos_llm", ["necessita_revisao"], unique=False)


def downgrade() -> None:
    """Downgrade schema - remover tabela enriquecimentos_llm."""
    op.drop_index("ix_enriquecimentos_revisao", table_name="enriquecimentos_llm")
    op.drop_index("ix_enriquecimentos_confianca", table_name="enriquecimentos_llm")
    op.drop_index("ix_enriquecimentos_proposicao", table_name="enriquecimentos_llm")
    op.drop_table("enriquecimentos_llm")
