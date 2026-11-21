import datetime
import re

from pydantic import BaseModel, Field, HttpUrl, PositiveInt, field_validator
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models
from app.schemas import InstructionSection
from util.recipe_normalization import FACTORS, ingredient_key, instruction_sections, plain_text


class IngredientLine(BaseModel):
    name: str = Field(min_length=1)
    external_id: str | None = None
    category: str | None = None
    original: str | None = None
    preparation: str | None = None
    quantity: str | None = None
    unit: str | None = None
    metric_quantity: str | None = None
    metric_unit: str | None = None


def free_text_line(text):
    wording = plain_text(text)
    name, _, preparation = wording.partition(",")
    # Recognize a leading measure only when a separate ingredient name follows.
    number = r"(?:\d+\s+\d+/\d+|\d+/\d+|\d+(?:\.\d+)?)"
    match = re.fullmatch(rf"({number}(?:\s*(?:-|\u2013|to)\s*{number})?)\s+(.+)", name)
    quantity = unit = None
    if match:
        quantity, name = match.groups()
        token, _, rest = name.partition(" ")
        if rest and token.casefold() in FACTORS.keys() | {"cup", "cups", "tbsp", "tsp", "tablespoon", "tablespoons", "teaspoon", "teaspoons"}:
            unit, name = token, rest
    return IngredientLine(name=name.strip() or wording, original=text, preparation=preparation.strip() or None,
                          quantity=quantity, unit=unit)


class ImportedRecipe(BaseModel):
    provider: str = Field(min_length=1)
    external_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    image_url: HttpUrl | None = None
    source_url: HttpUrl | None = None
    description: str | None = None
    cooking_time: PositiveInt | None = None
    servings: PositiveInt | None = None
    sections: list[InstructionSection] = Field(default_factory=list)
    lines: list[IngredientLine] = Field(default_factory=list)
    diets: list[str] = Field(default_factory=list)
    meal_types: list[str] = Field(default_factory=list)

    @field_validator("image_url", "source_url", mode="before")
    @classmethod
    def usable_url(cls, value):
        return value if value and str(value).lower().startswith(("https://", "http://")) else None


def spoonacular_line(data):
    metric = (data.get("measures") or {}).get("metric") or {}
    metric_unit = metric.get("unitShort") or ""
    use_metric = metric_unit.lower() in {"mg", "g", "kg", "ml", "l"} and metric.get("amount") is not None
    return IngredientLine(
        name=plain_text(data.get("nameClean") or data.get("name") or data.get("original")),
        original=data.get("original"), preparation=", ".join(data.get("meta") or []) or None,
        external_id=str(data["id"]) if data.get("id") is not None else None,
        category=data.get("aisle"), unit=data.get("unit"),
        quantity=str(data["amount"]) if data.get("amount") is not None else None,
        metric_quantity=str(metric["amount"]) if use_metric else None,
        metric_unit=metric_unit if use_metric else None,
    )


def spoonacular_recipe(data):
    fields = {}
    for source, target in (("image", "image_url"), ("sourceUrl", "source_url"), ("summary", "description"),
                           ("dishTypes", "meal_types"), ("diets", "diets"), ("readyInMinutes", "cooking_time"),
                           ("servings", "servings")):
        if source in data:
            value = data[source]
            if target == "description":
                value = plain_text(value) or None
            if target in ("servings", "cooking_time") and (value or 0) <= 0:
                value = None
            fields[target] = value
    if "extendedIngredients" in data:
        fields["lines"] = [spoonacular_line(item) for item in data["extendedIngredients"]]
    sections = instruction_sections(data.get("analyzedInstructions")) or instruction_sections(data.get("instructions"))
    if sections:
        fields["sections"] = sections
    return ImportedRecipe(provider="spoonacular", external_id=str(data["id"]) if data["id"] is not None else "", title=plain_text(data["title"]), **fields)


def resolve_ingredient(db, provider, line):
    source = db.get(models.IngredientSource, (provider, line.external_id)) if line.external_id else None
    if source:
        return db.get(models.Ingredient, source.ingredient_id)
    key = ingredient_key(line.name)
    ingredient = db.scalar(select(models.Ingredient).where(models.Ingredient.lookup_key == key))
    if not ingredient:
        ingredient = models.Ingredient(name=line.name if ingredient_key(line.name) == line.name.casefold().strip() else key,
                                       category=line.category)
        db.add(ingredient)
        db.flush()
    if line.external_id:
        db.add(models.IngredientSource(provider=provider, external_id=line.external_id, ingredient_id=ingredient.id))
        db.flush()
    return ingredient


def tags(db, model, names):
    result = []
    for name in dict.fromkeys(" ".join(n.split()).casefold().replace("-", " ") for n in names if n.strip()):
        tag = db.scalar(select(model).where(func.replace(func.lower(model.name), "-", " ") == name))
        if not tag:
            tag = model(name=name.capitalize())
            db.add(tag)
            db.flush()
        result.append(tag)
    return result


def save_import(db: Session, data: ImportedRecipe, featured=None):
    connection = db.connection()
    if connection.dialect.name == "sqlite" and not connection.connection.driver_connection.in_transaction:
        # SQLite legacy transaction mode does not issue BEGIN for a SAVEPOINT.
        connection.exec_driver_sql("BEGIN IMMEDIATE")
    # A concurrent first insert may win any unique catalog or provider key.
    for attempt in range(3):
        try:
            with db.begin_nested():
                query = select(models.Recipe).where(models.Recipe.provider == data.provider,
                                                    models.Recipe.external_id == data.external_id)
                recipe = db.scalar(query.with_for_update().execution_options(populate_existing=True))
                if not recipe and data.provider == "spoonacular":
                    recipe = db.scalar(select(models.Recipe).where(models.Recipe.spoonacular_id == int(data.external_id)).with_for_update())
                if not recipe:
                    recipe = models.Recipe()
                    db.add(recipe)
                for key, value in data.model_dump(mode="json", exclude_unset=True,
                                                   exclude={"lines", "sections", "meal_types", "diets"}).items():
                    setattr(recipe, key, value)
                if data.provider == "spoonacular":
                    recipe.spoonacular_id = int(data.external_id)
                if featured is not None:
                    recipe.is_featured = featured
                if "lines" in data.model_fields_set:
                    recipe.recipe_ingredients = [
                        models.RecipeIngredient(position=index, ingredient_id=resolve_ingredient(db, data.provider, line).id,
                                                **line.model_dump(exclude={"external_id", "category", "name"}))
                        for index, line in enumerate(data.lines)
                    ]
                if "sections" in data.model_fields_set:
                    recipe.sections = [section.model_dump() for section in data.sections]
                    recipe.instructions = "\n".join(step for section in data.sections for step in section.steps)
                for key, model in (("meal_types", models.MealType), ("diets", models.Diet)):
                    if key in data.model_fields_set:
                        setattr(recipe, key, tags(db, model, getattr(data, key)))
                recipe.last_updated = datetime.datetime.now()
                db.flush()
            db.commit()
            return recipe
        except IntegrityError:
            if attempt == 2:
                raise
