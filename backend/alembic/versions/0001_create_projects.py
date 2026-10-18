"""create projects table

Revision ID: 0001
Revises:
Create Date: 2026-10-18
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("team_name", sa.String(length=120), nullable=False),
        sa.Column("hackathon", sa.String(length=120), nullable=False),
        sa.Column("track", sa.String(length=120), nullable=False, server_default="open"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="idea"),
        sa.Column("priority", sa.String(length=10), nullable=False, server_default="medium"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("deadline", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("projects")
