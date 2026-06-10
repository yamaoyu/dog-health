from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260604_000003"
down_revision = "20260520_000002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("dogs", "birthday", existing_type=sa.Date(), nullable=True)
    op.add_column("dogs", sa.Column("gender", sa.Text(), nullable=True))
    op.create_check_constraint(
        "ck_dogs_gender",
        "dogs",
        "gender IN ('male', 'female', 'unknown')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_dogs_gender", "dogs", type_="check")
    op.drop_column("dogs", "gender")
    op.alter_column("dogs", "birthday", existing_type=sa.Date(), nullable=False)
