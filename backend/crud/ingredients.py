from typing import Optional
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from app import models


def get_ingredient(db: Session, ingredient_id: int, ingredient_name: Optional[str] = None):
    """Get a single ingredient by id or name"""
    query = db.query(models.Ingredient)
    
    conditions = []
    if ingredient_id:
        conditions.extend([
            models.Ingredient.id == ingredient_id,
            models.Ingredient.spoonacular_id == ingredient_id
        ])
    if ingredient_name:
        conditions.append(
            func.lower(models.Ingredient.name) == func.lower(ingredient_name)
        )
    
    if conditions:
        query = query.filter(or_(*conditions))
    
    return query.first()

def create_local_ingredients_from_spoonacular_recipe(db: Session, data: dict):
    """Given a list of ingredients for a recipe, convert to the local `Ingredient` model"""
    # First try to find by spoonacular_id
    ingredient = get_ingredient(db, data["id"], data["name"])
    
    if ingredient:
        # Update existing ingredient
        # ingredient.name = data["name"]
        ingredient.category = data["aisle"]
        # Update spoonacular_id if it's not set
        if ingredient.spoonacular_id is None:
            ingredient.spoonacular_id = data["id"]
    else:
        # Create new ingredient if it doesn't exist
        ingredient = models.Ingredient(
            name=data["name"],
            category=data["aisle"],
            spoonacular_id=data["id"]
        )
        db.add(ingredient)
    
    db.commit()
    db.refresh(ingredient)

    return ingredient



def get_all_ingredients(db: Session):
    """Get all ingredients"""
    return db.query(models.Ingredient).all()