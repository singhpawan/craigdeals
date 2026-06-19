"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-06-19
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "scraped",
        sa.Column("year", sa.Integer, nullable=True),
        sa.Column("model", sa.String(50), nullable=True),
        sa.Column("price", sa.Integer, nullable=True),
        sa.Column("miles", sa.Integer, nullable=True),
        sa.Column("lat", sa.Float, nullable=True),
        sa.Column("lon", sa.Float, nullable=True),
        sa.Column("date", sa.String(50), nullable=True),
        sa.Column("area", sa.String(20), nullable=True),
        sa.Column("title", sa.Text, nullable=True),
        sa.Column("body", sa.Text, nullable=True),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("image_count", sa.Integer, nullable=True),
        sa.Column("url", sa.String(500), nullable=True),
        sa.UniqueConstraint("url", "area", name="uq_scraped_url_area"),
    )
    op.create_index("ix_scraped_model", "scraped", ["model"])
    op.create_index("ix_scraped_area", "scraped", ["area"])

    op.create_table(
        "priced",
        sa.Column("year", sa.Integer, nullable=True),
        sa.Column("model", sa.String(50), nullable=True),
        sa.Column("price", sa.Integer, nullable=True),
        sa.Column("miles", sa.Integer, nullable=True),
        sa.Column("lat", sa.Float, nullable=True),
        sa.Column("lon", sa.Float, nullable=True),
        sa.Column("date", sa.String(50), nullable=True),
        sa.Column("area", sa.String(20), nullable=True),
        sa.Column("title", sa.Text, nullable=True),
        sa.Column("body", sa.Text, nullable=True),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("image_count", sa.Integer, nullable=True),
        sa.Column("url", sa.String(500), nullable=True),
        sa.Column("on_web", sa.Boolean, nullable=True),
        sa.Column("delta", sa.Float, nullable=True),
    )
    op.create_index("ix_priced_model", "priced", ["model"])
    op.create_index("ix_priced_delta", "priced", ["delta"])


def downgrade() -> None:
    op.drop_table("priced")
    op.drop_table("scraped")
