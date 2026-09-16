"""initial waiting list schema"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("restaurants", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(120), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("queue_entries", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("restaurant_id", sa.Integer(), sa.ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False), sa.Column("name", sa.String(120), nullable=False), sa.Column("phone", sa.String(30), nullable=False), sa.Column("party_size", sa.Integer(), nullable=False), sa.Column("status", sa.String(20), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("called_at", sa.DateTime(timezone=True), nullable=True), sa.CheckConstraint("party_size BETWEEN 1 AND 20", name="ck_queue_entries_party_size"), sa.CheckConstraint("status IN ('WAITING', 'CALLED')", name="ck_queue_entries_status"))
    op.create_index("ix_queue_entries_restaurant_status_created", "queue_entries", ["restaurant_id", "status", "created_at"])

def downgrade():
    op.drop_index("ix_queue_entries_restaurant_status_created", table_name="queue_entries")
    op.drop_table("queue_entries")
    op.drop_table("restaurants")
