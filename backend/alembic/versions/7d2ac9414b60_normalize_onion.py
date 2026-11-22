"""Use one catalog identity for onion and onions while preserving recipe lines."""
from alembic import op
import sqlalchemy as sa

revision = "7d2ac9414b60"
down_revision = "e51a63f22812"
branch_labels = None
depends_on = None


def upgrade():
    db = op.get_bind()
    ids = dict(db.execute(sa.text(
        "SELECT lookup_key, id FROM ingredients WHERE lookup_key IN ('onion', 'onions')"
    )).all())
    if "onions" not in ids:
        return
    if "onion" not in ids:
        db.execute(sa.text("UPDATE ingredients SET lookup_key='onion' WHERE id=:onions"), ids)
        return
    for table in ("recipe_ingredient", "ingredient_sources"):
        db.execute(sa.text(f"UPDATE {table} SET ingredient_id=:onion WHERE ingredient_id=:onions"), ids)
    db.execute(sa.text("DELETE FROM ingredients WHERE id=:onions"), ids)


def downgrade():
    # The previous schema accepts the merged catalog. Original line assignments cannot be inferred.
    pass
