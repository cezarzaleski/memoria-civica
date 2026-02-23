"""add_gastos_table

Revision ID: 009
Revises: 008
Create Date: 2026-02-22 00:00:00.000000

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
    """Upgrade schema - criar tabela gastos com constraints e índices de consulta."""
    op.create_table(
        "gastos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("deputado_id", sa.Integer(), nullable=True),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("mes", sa.Integer(), nullable=False),
        sa.Column("tipo_despesa", sa.String(length=255), nullable=False),
        sa.Column("tipo_documento", sa.String(length=50), nullable=True),
        sa.Column("data_documento", sa.Date(), nullable=True),
        sa.Column("numero_documento", sa.String(length=100), nullable=True),
        sa.Column("valor_documento", sa.Numeric(12, 2), server_default=sa.text("0"), nullable=False),
        sa.Column("valor_liquido", sa.Numeric(12, 2), server_default=sa.text("0"), nullable=False),
        sa.Column("valor_glosa", sa.Numeric(12, 2), server_default=sa.text("0"), nullable=False),
        sa.Column("nome_fornecedor", sa.String(length=255), nullable=True),
        sa.Column("cnpj_cpf_fornecedor", sa.String(length=20), nullable=True),
        sa.Column("url_documento", sa.Text(), nullable=True),
        sa.Column("cod_documento", sa.Integer(), nullable=True),
        sa.Column("cod_lote", sa.Integer(), nullable=True),
        sa.Column("parcela", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.ForeignKeyConstraint(["deputado_id"], ["deputados.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "deputado_id",
            "ano",
            "mes",
            "tipo_despesa",
            "cnpj_cpf_fornecedor",
            "numero_documento",
            name="uq_gasto",
        ),
    )

    op.create_index(
        "ux_gastos_dedup_normalized",
        "gastos",
        [
            sa.text("coalesce(deputado_id, -1)"),
            "ano",
            "mes",
            "tipo_despesa",
            sa.text("coalesce(cnpj_cpf_fornecedor, '')"),
            sa.text("coalesce(numero_documento, '')"),
        ],
        unique=True,
    )
    op.create_index("ix_gastos_deputado_id", "gastos", ["deputado_id"], unique=False)
    op.create_index("ix_gastos_ano_mes", "gastos", ["ano", "mes"], unique=False)
    op.create_index("ix_gastos_tipo_despesa", "gastos", ["tipo_despesa"], unique=False)
    op.create_index("ix_gastos_fornecedor", "gastos", ["cnpj_cpf_fornecedor"], unique=False)


def downgrade() -> None:
    """Downgrade schema - remover tabela gastos e artefatos associados."""
    op.drop_index("ix_gastos_fornecedor", table_name="gastos")
    op.drop_index("ix_gastos_tipo_despesa", table_name="gastos")
    op.drop_index("ix_gastos_ano_mes", table_name="gastos")
    op.drop_index("ix_gastos_deputado_id", table_name="gastos")
    op.drop_index("ux_gastos_dedup_normalized", table_name="gastos")
    op.drop_table("gastos")
