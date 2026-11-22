"""Resolve fridge items and normalize ingredient keys while retaining catalog IDs."""
from alembic import op
import sqlalchemy as sa

from util.ingredient_names_v1 import ingredient_key

revision = "a24f972c8b16"
down_revision = "7d2ac9414b60"
branch_labels = None
depends_on = None


def upgrade():
    db = op.get_bind()
    rows = db.execute(sa.text("SELECT id, name, lookup_key FROM ingredients ORDER BY id")).all()
    targets = {}
    for row in rows:
        key = ingredient_key(row.lookup_key)
        if key in targets:
            raise RuntimeError(f"Review ingredient collision before migration: {targets[key]} and {row.id} ({key})")
        targets[key] = row.id

    with op.batch_alter_table("fridge_items") as batch:
        batch.add_column(sa.Column("ingredient_id", sa.Integer(), nullable=True))
        batch.create_foreign_key("fk_fridge_ingredient", "ingredients", ["ingredient_id"], ["id"])

    for row in rows:
        key = ingredient_key(row.lookup_key)
        if key != row.lookup_key:
            db.execute(sa.text("UPDATE ingredients SET lookup_key=:key, name=:key WHERE id=:id"),
                       {"key": key, "id": row.id})
    for row in db.execute(sa.text("SELECT id, name FROM fridge_items")).all():
        target = targets.get(ingredient_key(row.name or ""))
        if target is not None:
            db.execute(sa.text("UPDATE fridge_items SET ingredient_id=:target WHERE id=:id"),
                       {"target": target, "id": row.id})


def downgrade():
    with op.batch_alter_table("fridge_items") as batch:
        batch.drop_constraint("fk_fridge_ingredient", type_="foreignkey")
        batch.drop_column("ingredient_id")
