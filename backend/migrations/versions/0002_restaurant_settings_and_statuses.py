"""add restaurant settings and queue lifecycle fields"""
from alembic import op
import sqlalchemy as sa

revision = "0002_restaurant_settings_and_statuses"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("restaurants") as batch:
        batch.add_column(sa.Column("country_code", sa.String(2), nullable=False, server_default="PE"))
        batch.add_column(sa.Column("phone_country_code", sa.String(4), nullable=False, server_default="+51"))
        batch.add_column(sa.Column("timezone", sa.String(64), nullable=False, server_default="America/Lima"))
    with op.batch_alter_table("queue_entries", recreate="always") as batch:
        batch.add_column(sa.Column("seated_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True))
        batch.drop_constraint("ck_queue_entries_status", type_="check")
        batch.create_check_constraint("ck_queue_entries_status", "status IN ('WAITING', 'CALLED', 'SEATED', 'CANCELLED', 'NO_SHOW')")


def downgrade():
    with op.batch_alter_table("queue_entries", recreate="always") as batch:
        batch.drop_constraint("ck_queue_entries_status", type_="check")
        batch.create_check_constraint("ck_queue_entries_status", "status IN ('WAITING', 'CALLED')")
        batch.drop_column("cancelled_at")
        batch.drop_column("seated_at")
    with op.batch_alter_table("restaurants") as batch:
        batch.drop_column("timezone")
        batch.drop_column("phone_country_code")
        batch.drop_column("country_code")
