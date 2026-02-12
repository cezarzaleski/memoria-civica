"""alter_votacoes_add_columns

Revision ID: 005
Revises: 004
Create Date: 2026-02-12 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: str | Sequence[str] | None = "004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema - tornar proposicao_id nullable e adicionar 6 novas colunas à tabela votacoes."""
    # Tornar proposicao_id nullable
    with op.batch_alter_table("votacoes") as batch_op:
        batch_op.alter_column(
            "proposicao_id",
            existing_type=sa.Integer(),
            nullable=True,
        )

    # Adicionar novas colunas
    op.add_column("votacoes", sa.Column("eh_nominal", sa.Boolean(), server_default=sa.text("0"), nullable=False))
    op.add_column("votacoes", sa.Column("votos_sim", sa.Integer(), server_default=sa.text("0"), nullable=False))
    op.add_column("votacoes", sa.Column("votos_nao", sa.Integer(), server_default=sa.text("0"), nullable=False))
    op.add_column("votacoes", sa.Column("votos_outros", sa.Integer(), server_default=sa.text("0"), nullable=False))
    op.add_column("votacoes", sa.Column("descricao", sa.Text(), nullable=True))
    op.add_column("votacoes", sa.Column("sigla_orgao", sa.String(50), nullable=True))

    # Adicionar índice em eh_nominal
    op.create_index("ix_votacoes_nominal", "votacoes", ["eh_nominal"], unique=False)


def downgrade() -> None:
    """Downgrade schema - remover colunas novas e restaurar proposicao_id como NOT NULL.

    ATENÇÃO: Se existirem votações com proposicao_id IS NULL, o downgrade falhará.
    Nesse caso, execute antes:
        DELETE FROM votacoes WHERE proposicao_id IS NULL;
    """
    # Remover índice
    op.drop_index("ix_votacoes_nominal", table_name="votacoes")

    # Remover colunas novas
    op.drop_column("votacoes", "sigla_orgao")
    op.drop_column("votacoes", "descricao")
    op.drop_column("votacoes", "votos_outros")
    op.drop_column("votacoes", "votos_nao")
    op.drop_column("votacoes", "votos_sim")
    op.drop_column("votacoes", "eh_nominal")

    # Restaurar proposicao_id como NOT NULL
    with op.batch_alter_table("votacoes") as batch_op:
        batch_op.alter_column(
            "proposicao_id",
            existing_type=sa.Integer(),
            nullable=False,
        )
