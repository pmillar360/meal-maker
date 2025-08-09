from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from . import models, schemas

def get_recipe(db: Session, recipe_id: int):
    """Get a single recipe by id with all details"""
    return db.query(models.Recipe).filter(
    or_(
        models.Recipe.id == recipe_id,
        models.Recipe.spoonacular_id == recipe_id
    )
).first()


def create_local_recipe_from_spoonacular(db: Session, data: dict):
    """Given an external object, convert to local db model"""
    recipe = (
        db.query(models.Recipe)
        .filter(models.Recipe.spoonacular_id == data["id"])
        .first()
    )

    if recipe:
        recipe.title = data["title"]
        recipe.image_url = data["image"]
        recipe.description = data["summary"]
        recipe.servings = data["servings"]
        recipe.cooking_time = data["readyInMinutes"]

    else:
        recipe = models.Recipe(
            title=data["title"],
            image_url=data["image"],
            description=data["summary"],
            servings=data["servings"],
            spoonacular_id=data["id"],
            cooking_time=data["readyInMinutes"],
        )
        db.add(recipe)
    
    for ingredientData in data["extendedIngredients"]:
        ingredient = create_local_ingredients_from_spoonacular_recipe(db, ingredientData, False)

        recipeIngredient = models.RecipeIngredient(
            ingredient = ingredient,
            quantity=str(ingredientData["amount"]),
            unit=ingredientData["unit"]
        )

        recipe.recipe_ingredients.append(recipeIngredient)

    db.commit()
    db.refresh(recipe)

    return recipe


def create_local_ingredients_from_spoonacular_recipe(db: Session, data: dict, commit: bool = True):
    """Given a list of ingredients for a recipe, convert to the local `Ingredient` model"""
    ingredient = (
        db.query(models.Ingredient)
        .filter(models.Ingredient.spoonacular_id == data["id"])
        .first()
    )

    if ingredient:
        ingredient.name = data["name"]
        ingredient.category = data["aisle"]
    else:
        ingredient = models.Ingredient(
            name=data["name"],
            category=data["aisle"],
            spoonacular_id=data["id"]
        )

        db.add(ingredient)
    
    if commit:
        db.commit()
        db.refresh(ingredient)
    else:
        db.flush()

    return ingredient

def get_recipes(
    db: Session, 
    ingredients: List[str] = [], 
    meal_type: Optional[str] = None, 
    diet: Optional[str] = None,
    skip: int = 0, 
    limit: int = 100
):
    """Get recipes with optional filtering"""
    query = db.query(models.Recipe)
    
    # Apply meal type filter
    if meal_type:
        query = query.filter(models.Recipe.meal_type == meal_type)
    
    # Apply dietary filter
    if diet:
        diet_obj = db.query(models.Diet).filter(models.Diet.name == diet).first()
        if diet_obj:
            query = query.filter(models.Recipe.diets.contains(diet_obj))
    
    # Apply ingredient filter if ingredients are provided
    if ingredients:
        for ingredient_name in ingredients:
            ingredient = db.query(models.Ingredient).filter(
                models.Ingredient.name.ilike(f"%{ingredient_name.strip()}%")
            ).first()
            if ingredient:
                query = query.join(models.Recipe.recipe_ingredients).filter(models.RecipeIngredient.ingredient_id == ingredient.id)
    
    return query.offset(skip).limit(limit).all()

def get_all_ingredients(db: Session):
    """Get all ingredients"""
    return db.query(models.Ingredient).all()

def add_shopping_list_item(db: Session, item: schemas.ShoppingListItemCreate):
    """Add item to shopping list"""
    db_item = models.ShoppingListItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_shopping_list(db: Session, skip: int = 0, limit: int = 100):
    """Get all shopping list items"""
    return db.query(models.ShoppingListItem).offset(skip).limit(limit).all()

def update_shopping_list_item(db: Session, item_id: int, item_update: schemas.ShoppingListItemUpdate):
    """Update shopping list item status or quantity"""
    db_item = db.query(models.ShoppingListItem).filter(models.ShoppingListItem.id == item_id).first()
    if db_item:
        update_data = item_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_item, key, value)
        db.commit()
        db.refresh(db_item)
    return db_item

def delete_shopping_list_item(db: Session, item_id: int):
    """Delete shopping list item"""
    db_item = db.query(models.ShoppingListItem).filter(models.ShoppingListItem.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
        return True
    return False
