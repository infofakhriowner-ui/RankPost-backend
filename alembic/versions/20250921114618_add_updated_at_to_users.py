from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20250921114618"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add updated_at if it doesn't exist. SQLite has no IF NOT EXISTS for columns,
    # so we try to add and ignore if already exists by catching exception at runtime (Alembic can't catch here).
    try:
        op.add_column("users", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))
    except Exception:
        pass

    # Set current timestamp for NULLs to avoid issues
    conn = op.get_bind()
    try:
        conn.execute(sa.text("UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL"))
    except Exception:
        pass

def downgrade():
    try:
        op.drop_column("users", "updated_at")
    except Exception:
        pass
