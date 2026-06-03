"""make user optional fields nullable

Revision ID: 7f2c9d4a1b8e
Revises: ee7433a0ea4c
Create Date: 2026-06-03 15:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7f2c9d4a1b8e"
down_revision: Union[str, Sequence[str], None] = "ee7433a0ea4c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "last_name",
            existing_type=sa.String(),
            nullable=True,
        )
        batch_op.alter_column(
            "username",
            existing_type=sa.String(),
            nullable=True,
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "username",
            existing_type=sa.String(),
            nullable=False,
        )
        batch_op.alter_column(
            "last_name",
            existing_type=sa.String(),
            nullable=False,
        )
