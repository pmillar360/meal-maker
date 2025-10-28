import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from . import models, schemas
from util.spoonacular import get_random_recipes

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
    """Get a set number of \"random\" recipes from the database or Spoonacular API"""

    twenty_four_hours_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=24)
    featured_recipes = (
        db.query(models.Recipe)
        .filter(models.Recipe.is_featured == True, models.Recipe.last_updated >= twenty_four_hours_ago)
        .limit(number)
        .all()
    )


    if featured_recipes:
        return featured_recipes # The recipes for the day are cached
    
    try:
        # TODO log fetching recipes from spoonacular
        random_recipes_result = get_random_recipes(number) # Make API request for random recipes

        if not random_recipes_result["recipes"]:
            return featured_recipes[:number] # If no recipes found then return old ones

        featured_recipes = (
            db.query(models.Recipe)
            .filter(models.Recipe.is_featured == True)
            .all()
        )

        for recipe in featured_recipes: # Don't feature old recipes
            recipe.is_featured = False

        cached_recipes = []

        for recipe in random_recipes_result["recipes"]:
            try:
                cached_recipe = create_local_recipe_from_spoonacular(db, recipe, True) # Recipe will be added or updated in the DB
                cached_recipes.append(cached_recipe)
            except Exception as e:
                print(f"Error caching recipe: {e}")
                continue

        return cached_recipes
    
    except Exception as e:
        print(f"Error fetching featured recipes: {e}")

        return (
            db.query(models.Recipe)
            .filter(models.Recipe.is_featured == True)
            .limit(number)
            .all()
        )

def create_local_recipe_from_spoonacular(db: Session, data: dict, is_featured_new: bool = False):
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
        recipe.is_featured = is_featured_new

    else:
        recipe = models.Recipe(
            title=data["title"],
            image_url=data["image"],
            description=data["summary"],
            servings=data["servings"],
            spoonacular_id=data["id"],
            cooking_time=data["readyInMinutes"],
            is_featured = is_featured_new,
        )
        db.add(recipe)
        db.flush()

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

    for meal_type in data.get("dishTypes", []):
        local_meal_type = (
            db.query(models.MealType)
            .filter(func.lower(models.MealType.name) == func.lower(meal_type))
            .first()
        )

        if local_meal_type is None:
            local_meal_type = models.MealType(
                name=meal_type,
            )
            db.add(local_meal_type)
            db.flush()

        recipe.meal_types.append(local_meal_type)
        pass

    for diet_type in data.get("diets", []):
        local_diet = (
            db.query(models.Diet)
            .filter(func.lower(models.Diet.name) == func.lower(diet_type))
            .first()
        )

        if local_diet is None:
            local_diet = models.Diet(
                name=diet_type,
            )
            db.add(local_diet)
            db.flush()

        recipe.diets.append(local_diet)
        pass

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
        meal_type_obj = db.query(models.MealType).filter(models.MealType.name == meal_type).first()
        if meal_type_obj:
            query = query.filter(models.Recipe.diets.contains(meal_type_obj))
    
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

def get_all_diets(db: Session):
    """Get all diets"""
    return db.query(models.Diet).all()

def get_all_meal_types(db:Session):
    """Get all meal types"""
    return db.query(models.MealType).all()

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
