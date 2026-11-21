from sqlalchemy.orm import Session
from app import models
from crud.recipe_import import resolve_ingredient, spoonacular_line
from util.recipe_normalization import ingredient_key


def get_ingredient(db: Session, ingredient_id: int, ingredient_name=None):
    if ingredient_id:
        return db.get(models.Ingredient, ingredient_id)
    if ingredient_name:
        return db.query(models.Ingredient).filter_by(lookup_key=ingredient_key(ingredient_name)).first()


def create_local_ingredients_from_spoonacular_recipe(db: Session, data: dict):
    ingredient = resolve_ingredient(db, "spoonacular", spoonacular_line(data))
    db.commit()
    return ingredient


def get_all_ingredients(db: Session):
    """Get all ingredients"""
    return db.query(models.Ingredient).all()