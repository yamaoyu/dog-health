from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260520_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    op.create_table(
        "owners",
        sa.Column(
            "owner_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("owner_id"),
    )

    op.create_table(
        "dogs",
        sa.Column(
            "dog_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("birthday", sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint("dog_id"),
    )

    op.create_table(
        "owner_dogs",
        sa.Column(
            "owner_dog_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dog_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["dog_id"], ["dogs.dog_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_id"], ["owners.owner_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("owner_dog_id"),
        sa.UniqueConstraint("owner_id", "dog_id", name="uq_owner_dogs_owner_id_dog_id"),
    )


def downgrade() -> None:
    op.drop_table("owner_dogs")
    op.drop_table("dogs")
    op.drop_table("owners")
