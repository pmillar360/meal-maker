"""Preserve local recipe IDs and split catalog identities from ordered lines."""
from alembic import op
import sqlalchemy as sa

revision = "e51a63f22812"
down_revision = "bf25903c8d51"
branch_labels = None
depends_on = None


def upgrade():
    db = op.get_bind()
    for name in ("provider", "external_id", "source_url"):
        op.add_column("recipes", sa.Column(name, sa.String()))
    op.add_column("recipes", sa.Column("sections", sa.JSON()))
    op.create_index("uq_recipe_source", "recipes", ["provider", "external_id"], unique=True)
    op.execute("UPDATE recipes SET provider='spoonacular', external_id=CAST(spoonacular_id AS VARCHAR) WHERE spoonacular_id IS NOT NULL")
    op.add_column("ingredients", sa.Column("lookup_key", sa.String()))
    sources = op.create_table(
        "ingredient_sources",
        sa.Column("provider", sa.String(), primary_key=True),
        sa.Column("external_id", sa.String(), primary_key=True),
        sa.Column("ingredient_id", sa.Integer(), sa.ForeignKey("ingredients.id"), nullable=False),
    )
    lines = op.create_table(
        "ordered_recipe_lines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id"), nullable=False),
        sa.Column("ingredient_id", sa.Integer(), sa.ForeignKey("ingredients.id"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("original", sa.Text()), sa.Column("preparation", sa.Text()),
        *[sa.Column(name, sa.String()) for name in ("quantity", "unit", "metric_quantity", "metric_unit")],
    )
    canonical = {}
    redirects = {}
    for row in db.execute(sa.text("SELECT id, name, spoonacular_id FROM ingredients ORDER BY id")).mappings():
        key = " ".join((row["name"] or "").casefold().split())
        if key in ("scallions", "scallion", "green onions"):
            key = "green onion"
        target = canonical.setdefault(key, row["id"])
        redirects[row["id"]] = target
        if target == row["id"]:
            db.execute(sa.text("UPDATE ingredients SET lookup_key=:key WHERE id=:id"), dict(key=key, id=target))
        if row["spoonacular_id"] is not None:
            db.execute(sources.insert().values(provider="spoonacular", external_id=str(row["spoonacular_id"]), ingredient_id=target))
    for row in db.execute(sa.text("SELECT * FROM recipe_ingredient ORDER BY recipe_id, ingredient_id")).mappings():
        db.execute(lines.insert().values(**dict(row, position=row["ingredient_id"], ingredient_id=redirects[row["ingredient_id"]])))
    op.drop_table("recipe_ingredient")
    op.rename_table("ordered_recipe_lines", "recipe_ingredient")
    op.create_index("ix_recipe_ingredient_recipe_id", "recipe_ingredient", ["recipe_id"])
    for old, target in redirects.items():
        if old != target:
            db.execute(sa.text("DELETE FROM ingredients WHERE id=:id"), dict(id=old))
    with op.batch_alter_table("ingredients") as batch:
        batch.alter_column("lookup_key", existing_type=sa.String(), nullable=False)
        batch.create_unique_constraint("uq_ingredient_lookup_key", ["lookup_key"])


def downgrade():
    db = op.get_bind()
    repeated = db.execute(sa.text("SELECT 1 FROM recipe_ingredient GROUP BY recipe_id, ingredient_id HAVING COUNT(*) > 1")).first()
    other_source = db.execute(sa.text("SELECT 1 FROM recipes WHERE provider <> 'spoonacular'")).first()
    if repeated or other_source:
        raise RuntimeError("Downgrade would discard repeated lines or provider identities. Restore a pre-upgrade backup.")
    restored_ids = {}
    sources = db.execute(sa.text(
        "SELECT s.ingredient_id, s.provider, s.external_id, i.spoonacular_id "
        "FROM ingredient_sources s JOIN ingredients i ON i.id = s.ingredient_id"
    ))
    for ingredient_id, provider, external_id, legacy_id in sources:
        try:
            source_id = int(external_id)
        except ValueError:
            source_id = None
        if (provider != "spoonacular" or source_id is None or str(source_id) != external_id
                or not -(2**31) <= source_id < 2**31 or ingredient_id in restored_ids
                or legacy_id not in (None, source_id)):
            raise RuntimeError("Downgrade would discard ingredient provider identities. Restore a pre-upgrade backup.")
        restored_ids[ingredient_id] = source_id
    if restored_ids:
        db.execute(sa.text("UPDATE ingredients SET spoonacular_id=:source_id WHERE id=:ingredient_id"),
                   [dict(ingredient_id=key, source_id=value) for key, value in restored_ids.items()])
    op.create_table(
        "legacy_recipe_lines",
        sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id"), primary_key=True),
        sa.Column("ingredient_id", sa.Integer(), sa.ForeignKey("ingredients.id"), primary_key=True),
        sa.Column("quantity", sa.String()), sa.Column("unit", sa.String()),
    )
    op.execute("INSERT INTO legacy_recipe_lines SELECT recipe_id, ingredient_id, quantity, unit FROM recipe_ingredient")
    op.drop_table("recipe_ingredient")
    op.rename_table("legacy_recipe_lines", "recipe_ingredient")
    op.drop_table("ingredient_sources")
    with op.batch_alter_table("ingredients") as batch:
        batch.drop_constraint("uq_ingredient_lookup_key", type_="unique")
        batch.drop_column("lookup_key")
    op.drop_index("uq_recipe_source", table_name="recipes")
    for name in ("sections", "source_url", "external_id", "provider"):
        op.drop_column("recipes", name)
