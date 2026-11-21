import datetime
from typing import List, Optional
from fastapi import HTTPException
from requests.exceptions import RequestException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from crud.recipe_import import save_import, spoonacular_recipe, ImportedRecipe
from util.recipe_normalization import ingredient_key, instruction_sections
from util.logger import log
from util.spoonacular import get_external_recipe_by_id, get_random_recipes, get_recipe_instructions, get_recipes_by_ingredients as get_recipes_by_ingredients_external


def _normalize_ingredient_name(name: str) -> str:
    return ingredient_key(name or "")


def _normalized_ingredient_names(ingredients: List[str]) -> set[str]:
    return {_normalize_ingredient_name(name) for name in ingredients if name.strip()}


def _get_user_fridge_name_set(db: Session, user_id: int) -> set[str]:
    fridge_items = db.query(models.FridgeItem).filter(models.FridgeItem.user_id == user_id).all()
    return {
        _normalize_ingredient_name(item.name)
        for item in fridge_items
        if _normalize_ingredient_name(item.name)
    }


def _build_ingredient_statuses(recipe: models.Recipe, fridge_name_set: set[str]):
    ingredient_statuses = []
    missing_recipe_ingredients = []

    seen = set()
    for recipe_ingredient in recipe.recipe_ingredients:
        if recipe_ingredient.ingredient_id in seen:
            continue
        seen.add(recipe_ingredient.ingredient_id)
        ingredient_name = _normalize_ingredient_name(recipe_ingredient.ingredient.name)
        has_in_fridge = ingredient_name in fridge_name_set

        ingredient_statuses.append({
            "ingredient": recipe_ingredient.ingredient,
            "quantity": recipe_ingredient.quantity,
            "unit": recipe_ingredient.unit,
            "has_in_fridge": has_in_fridge,
            "missing": not has_in_fridge,
        })

        if not has_in_fridge:
            missing_recipe_ingredients.append(recipe_ingredient)

    return ingredient_statuses, missing_recipe_ingredients

def get_recipe_by_id(db: Session, recipe_id: int):
    recipe = db.get(models.Recipe, recipe_id)
    
    old_date = datetime.datetime.now() - datetime.timedelta(days=30)

    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    if recipe.spoonacular_id is not None and (recipe.last_updated is None or recipe.last_updated < old_date):
        # logger.info(f"Making external API request for spooancular ID: {recipe.spoonacular_id}")
        try:
            external_data = get_external_recipe_by_id(recipe.spoonacular_id)
        except RequestException as error:
            log(f"Spoonacular recipe refresh failed: {type(error).__name__}", level=30)
            return recipe

        if external_data:
            try:
                recipe = create_local_recipe_from_spoonacular(db, external_data)
            except (ValueError, KeyError, TypeError) as error:
                log(f"Invalid Spoonacular refresh: {type(error).__name__}", level=30)
                return recipe

    if recipe.spoonacular_id is not None and recipe.instructions is None:
        try:
            sections = get_recipe_instructions(recipe.spoonacular_id)
        except RequestException as error:
            log(f"Spoonacular instructions request failed: {type(error).__name__}", level=30)
            return recipe
        recipe = save_import(db, ImportedRecipe(provider="spoonacular", external_id=str(recipe.spoonacular_id),
                                                 title=recipe.title, sections=instruction_sections(sections)))

    return recipe

def get_recipes(
    db: Session, 
    ingredients: Optional[List[str]] = None,
    meal_types: Optional[List[str]] = None, 
    diet: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0, 
    limit: int = 100,
    *,
    ingredient_ids: Optional[List[int]] = None,
):
    """Get recipes with optional filtering"""
    query = db.query(models.Recipe)
    
    # Apply meal type filter
    if meal_types:
        for meal_type_name in meal_types:
            meal_type = db.query(models.MealType).filter(
                models.MealType.name.ilike(f"%{meal_type_name.strip()}%")
            ).first()
            if meal_type:
                query = query.filter(models.Recipe.meal_types.contains(meal_type)) # TODO How to OR filter instead of AND?
    
    # Apply dietary filter
    if diet:
        diet_obj = db.query(models.Diet).filter(models.Diet.name == diet).first()
        if diet_obj:
            query = query.filter(models.Recipe.diets.contains(diet_obj))

    # Apply recipe title search filter
    if search and search.strip():
        query = query.filter(models.Recipe.title.ilike(f"%{search.strip()}%"))
    
    # Each selected ingredient must match its own recipe ingredient row.
    for ingredient_id in set(ingredient_ids or []):
        query = query.filter(models.Recipe.recipe_ingredients.any(
            models.RecipeIngredient.ingredient_id == ingredient_id
        ))
    for name in _normalized_ingredient_names(ingredients or []):
        query = query.filter(models.Recipe.recipe_ingredients.any(
            models.RecipeIngredient.ingredient.has(models.Ingredient.lookup_key == name)
        ))
    
    return query.offset(skip).limit(limit).all()

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
        log(f"Error fetching featured recipes: {type(e).__name__}", level=30)

        return (
            db.query(models.Recipe)
            .filter(models.Recipe.is_featured == True)
            .limit(number)
            .all()
        )

# TODO Check for duplicates when searching external recipes?
def get_recipe_suggestions_by_ingredients(db: Session, ingredient_names: List[str], number: int = 10, fetchExternal: bool = False):
    """Suggest recipes that use at least one on-hand ingredient."""
    query = db.query(models.Recipe)
    names = _normalized_ingredient_names(ingredient_names)
    if names:
        query = query.filter(models.Recipe.recipe_ingredients.any(
            models.RecipeIngredient.ingredient.has(models.Ingredient.lookup_key.in_(names))
        ))
    recipes = query.limit(number).all()

    # This is expensive on the API, so only do it if requested
    if len(recipes) < number and fetchExternal:
        # Fetch recipes from external API
        count = number - len(recipes)
        try:
            external_recipes = get_recipes_by_ingredients_external(ingredient_names, count)
        except RequestException as error:
            log(f"Spoonacular suggestions request failed: {type(error).__name__}", level=30)
            return recipes

        # Cache external recipes locally
        seen_external_ids = {recipe.spoonacular_id for recipe in recipes}
        for ext_recipe in external_recipes:
            try:
                external_id = ext_recipe["id"]
                if external_id in seen_external_ids:
                    continue
                local_recipe = create_local_recipe_from_spoonacular(db, get_external_recipe_by_id(external_id))
                recipes.append(local_recipe)
                seen_external_ids.add(external_id)
            except Exception as e:
                log(f"Error caching suggested recipe: {type(e).__name__}", level=30)
                continue
    
    return recipes


def get_recipes_with_fridge_availability(
    db: Session,
    user_id: int,
    ingredients: Optional[List[str]] = None,
    meal_types: Optional[List[str]] = None,
    diet: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    *,
    ingredient_ids: Optional[List[int]] = None,
):
    fridge_name_set = _get_user_fridge_name_set(db, user_id)
    recipe_list = get_recipes(db, ingredients, meal_types, diet, search, skip, limit, ingredient_ids=ingredient_ids)

    availability_summaries = []

    for recipe in recipe_list:
        ingredient_statuses, missing_recipe_ingredients = _build_ingredient_statuses(recipe, fridge_name_set)
        total_ingredients = len(ingredient_statuses)
        missing_count = len(missing_recipe_ingredients)

        availability_summaries.append({
            "recipe": recipe,
            "total_ingredients": total_ingredients,
            "available_ingredients": total_ingredients - missing_count,
            "missing_ingredients": missing_count,
            "missing_ingredient_names": [item.ingredient.name for item in missing_recipe_ingredients],
        })

    return availability_summaries


def get_recipe_availability_for_user(db: Session, user_id: int, recipe_id: int):
    recipe = get_recipe_by_id(db, recipe_id)
    fridge_name_set = _get_user_fridge_name_set(db, user_id)
    ingredient_statuses, missing_recipe_ingredients = _build_ingredient_statuses(recipe, fridge_name_set)
    total_ingredients = len(ingredient_statuses)
    missing_count = len(missing_recipe_ingredients)

    return {
        "recipe": recipe,
        "ingredient_statuses": ingredient_statuses,
        "total_ingredients": total_ingredients,
        "available_ingredients": total_ingredients - missing_count,
        "missing_ingredients": missing_count,
        "missing_ingredient_names": [item.ingredient.name for item in missing_recipe_ingredients],
    }


def get_missing_recipe_ingredients_for_user(db: Session, user_id: int, recipe_id: int):
    recipe = get_recipe_by_id(db, recipe_id)
    fridge_name_set = _get_user_fridge_name_set(db, user_id)
    _, missing_recipe_ingredients = _build_ingredient_statuses(recipe, fridge_name_set)
    missing_ids = {line.ingredient_id for line in missing_recipe_ingredients}
    return [line for line in recipe.recipe_ingredients if line.ingredient_id in missing_ids]

def create_local_recipe_from_spoonacular(db: Session, data: dict, is_featured_new=None):
    return save_import(db, spoonacular_recipe(data), is_featured_new)


def get_user_favourite_recipes(db: Session, user_id: int):
    """Get a user's favourite recipes"""
    favourite_recipes = db.query(models.Recipe).join(models.FavouriteRecipe).filter(
            models.FavouriteRecipe.user_id == user_id
        ).all()

    return favourite_recipes

def add_user_favourite_recipe(db: Session, user_id: int, recipe_id: int):
    """Add a recipe to a user's favourites"""
    favourite = db.query(models.FavouriteRecipe).filter(
        models.FavouriteRecipe.user_id == user_id,
        models.FavouriteRecipe.recipe_id == recipe_id
    ).first()

    if favourite:
        return favourite  # Already a favourite

    favourite = models.FavouriteRecipe(
        user_id=user_id,
        recipe_id=recipe_id
    )
    db.add(favourite)
    db.commit()
    db.refresh(favourite)
    return favourite

def remove_user_favourite_recipe(db: Session, user_id: int, recipe_id: int):
    """Remove a recipe from a user's favourites"""
    favourite = db.query(models.FavouriteRecipe).filter(
        models.FavouriteRecipe.user_id == user_id,
        models.FavouriteRecipe.recipe_id == recipe_id
    ).first()
    
    if favourite:
        db.delete(favourite)
        db.commit()
        return True
    return False

# NOTE These will be here for now...
def get_all_diets(db: Session):
    """Get all diets"""
    return db.query(models.Diet).all()

def get_all_meal_types(db:Session):
    """Get all meal types"""
    return db.query(models.MealType).all()
