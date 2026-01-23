"""initial_baseline

Revision ID: 0b0b45871666
Revises:
Create Date: 2026-01-23 16:20:20.880345

"""
from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = '0b0b45871666'
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
