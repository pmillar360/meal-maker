"""Enforce account identity and persist refresh sessions."""

from alembic import op
import sqlalchemy as sa

revision = "bf25903c8d51"
down_revision = "7bd3a31eecbf"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index("ix_users_username_lower", "users", [sa.text("lower(username)")], unique=True)
    op.add_column("users", sa.Column("auth_id", sa.String(32)))

    if op.get_context().dialect.name == "sqlite":
        op.drop_index("ix_users_username_lower", table_name="users")
        op.execute("UPDATE users SET auth_id = lower(hex(randomblob(16)))")
        with op.batch_alter_table("users") as batch:
            batch.alter_column("auth_id", existing_type=sa.String(32), nullable=False)
            batch.create_unique_constraint("uq_users_auth_id", ["auth_id"])
        op.create_index("ix_users_username_lower", "users", [sa.text("lower(username)")], unique=True)
    else:
        op.execute("UPDATE users SET auth_id = replace(gen_random_uuid()::text, '-', '')")
        op.alter_column("users", "auth_id", existing_type=sa.String(32), nullable=False)
        op.create_unique_constraint("uq_users_auth_id", "users", ["auth_id"])

    op.create_table(
        "refresh_sessions",
        sa.Column("token_hash", sa.String(64), primary_key=True),
        sa.Column("user_auth_id", sa.String(32), sa.ForeignKey("users.auth_id", ondelete="CASCADE"), nullable=False),
        sa.Column("expires_at", sa.BigInteger(), nullable=False),
    )
    op.create_index("ix_refresh_sessions_user_auth_id", "refresh_sessions", ["user_auth_id"])
    op.create_index("ix_refresh_sessions_expires_at", "refresh_sessions", ["expires_at"])


def downgrade():
    op.drop_table("refresh_sessions")
    op.drop_index("ix_users_username_lower", table_name="users")
    with op.batch_alter_table("users") as batch:
        batch.drop_constraint("uq_users_auth_id", type_="unique")
        batch.drop_column("auth_id")
