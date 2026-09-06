"""add global application settings"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

def upgrade():
    if "app_settings" in sa.inspect(op.get_bind()).get_table_names():
        return
    op.create_table(
        "app_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("key"),
    )
    op.create_index("ix_app_settings_key", "app_settings", ["key"], unique=True)

def downgrade():
    if "app_settings" not in sa.inspect(op.get_bind()).get_table_names():
        return
    op.drop_index("ix_app_settings_key", table_name="app_settings")
    op.drop_table("app_settings")
