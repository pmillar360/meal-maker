from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas

def get_recipe(db: Session, recipe_id: int):
    """Get a single recipe by id with all details"""
    return db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()

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
                query = query.filter(models.Recipe.ingredients.contains(ingredient))
    
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
        update_data = item_update.dict(exclude_unset=True)
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
