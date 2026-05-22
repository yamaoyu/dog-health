from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260520_000002"
down_revision = "20260520_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("owners", sa.Column("login_id", sa.Text(), nullable=True))
    op.execute("UPDATE owners SET login_id = owner_id::text WHERE login_id IS NULL")
    op.alter_column("owners", "login_id", nullable=False)
    op.create_unique_constraint("uq_owners_login_id", "owners", ["login_id"])


def downgrade() -> None:
    op.drop_constraint("uq_owners_login_id", "owners", type_="unique")
    op.drop_column("owners", "login_id")
