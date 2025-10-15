from sqlalchemy.orm import Session
from sqlalchemy import or_, func
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

def get_featured_recipes(db: Session, number: int):
    """Get a set number of \"random\" recipes from the database"""

    return get_recipes(db, ingredients=[], limit=number) # TODO For now just return the first items from the database. In the future we want to pick random numbers

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
        ingredient = create_local_ingredients_from_spoonacular_recipe(db, ingredientData)

        recipeIngredient = (
            db.query(models.RecipeIngredient)
            .filter(models.RecipeIngredient.ingredient_id == ingredient.id, models.RecipeIngredient.recipe_id == recipe.id)
            .first()
        )

        if recipeIngredient is None:
            recipeIngredient = models.RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient,
                quantity=str(ingredientData["amount"]),
                unit=ingredientData["unit"],
            )

        recipe.recipe_ingredients.append(recipeIngredient)

    db.commit()
    db.refresh(recipe)

    return recipe


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
