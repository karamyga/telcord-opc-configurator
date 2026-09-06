"""add explicit cable variants"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None

def upgrade():
    if "cable_variants" in sa.inspect(op.get_bind()).get_table_names():
        return
    op.create_table(
        "cable_variants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(128), nullable=False, unique=True),
        sa.Column("product_type", sa.String(16), nullable=False),
        sa.Column("fiber_type", sa.String(32), nullable=False),
        sa.Column("fiber_name", sa.String(64), nullable=False),
        sa.Column("construction", sa.String(32), nullable=False),
        sa.Column("jacket", sa.String(16), nullable=True),
        sa.Column("color", sa.String(32), nullable=True),
        sa.Column("color_code", sa.String(8), nullable=True),
        sa.Column("raw_price", sa.Numeric(14, 4), nullable=True),
        sa.Column("currency", sa.String(3), nullable=True),
        sa.Column("source", sa.Text(), nullable=True),
        sa.Column("available", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_cable_variants_key", "cable_variants", ["key"], unique=True)
    op.create_index("ix_cable_variants_fiber_type", "cable_variants", ["fiber_type"])
    op.create_index("ix_cable_variants_construction", "cable_variants", ["construction"])
    op.create_index("ix_cable_variants_available", "cable_variants", ["available"])

def downgrade():
    if "cable_variants" in sa.inspect(op.get_bind()).get_table_names():
        op.drop_table("cable_variants")
