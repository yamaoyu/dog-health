from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260627_000004"
down_revision = "20260604_000003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "event_types",
        sa.Column(
            "event_type_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.PrimaryKeyConstraint("event_type_id"),
        sa.UniqueConstraint("code", name="uq_event_types_code"),
    )

    event_types_table = sa.table(
        "event_types",
        sa.column("code", sa.Text()),
        sa.column("display_name", sa.Text()),
        sa.column("is_active", sa.Boolean()),
    )
    op.bulk_insert(
        event_types_table,
        [
            {"code": "walk", "display_name": "散歩", "is_active": True},
            {"code": "food", "display_name": "ご飯", "is_active": True},
            {"code": "toilet", "display_name": "トイレ", "is_active": True},
        ],
    )

    op.create_table(
        "events",
        sa.Column(
            "event_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("dog_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("memo", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["dog_id"], ["dogs.dog_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["event_type_id"], ["event_types.event_type_id"]),
        sa.PrimaryKeyConstraint("event_id"),
    )

    op.create_table(
        "walk_events",
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("distance", sa.Text(), nullable=True),
        sa.Column("time", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["event_id"], ["events.event_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("event_id"),
    )

    op.create_table(
        "food_events",
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("menu", sa.Text(), nullable=True),
        sa.Column("amount", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["event_id"], ["events.event_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("event_id"),
    )

    op.create_table(
        "toilet_events",
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.Text(), nullable=True),
        sa.Column("condition", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["event_id"], ["events.event_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("event_id"),
    )


def downgrade() -> None:
    op.drop_table("toilet_events")
    op.drop_table("food_events")
    op.drop_table("walk_events")
    op.drop_table("events")
    op.drop_table("event_types")
