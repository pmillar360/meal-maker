from fastapi import HTTPException
from util.recipe_normalization import ingredient_key
from sqlalchemy.orm import Session

from app import models, schemas

def add_fridge_item(db: Session, user_id: int, item: schemas.FridgeItemCreate):
    """Add item to the User's fridge"""
    db_item = models.FridgeItem(**item.model_dump())
    if item.ingredient_id is not None:
        ingredient = db.get(models.Ingredient, item.ingredient_id)
        if ingredient is None:
            raise HTTPException(422, "Unknown ingredient ID")
        db_item.name = ingredient.name
    else:
        db_item.ingredient_id = db.query(models.Ingredient.id).filter_by(lookup_key=ingredient_key(item.name)).scalar()
    db_item.user_id = user_id
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_fridge_items(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get the items in the User's fridge"""
    return db.query(models.FridgeItem).filter(models.FridgeItem.user_id == user_id).offset(skip).limit(limit).all()

def update_fridge_item(db: Session, user_id: int, item_id: int, item_update: schemas.FridgeItemUpdate):
    """Update an item in the User's fridge"""
    db_item = db.query(models.FridgeItem).filter(models.FridgeItem.id == item_id, models.FridgeItem.user_id == user_id).first()
    if db_item:
        update_data = item_update.model_dump(exclude_unset=True)
        if "name" in update_data:
            if update_data["name"] is None:
                raise HTTPException(422, "Ingredient name is required")
            update_data["ingredient_id"] = db.query(models.Ingredient.id).filter_by(lookup_key=ingredient_key(update_data["name"])).scalar()
        for key, value in update_data.items():
            setattr(db_item, key, value)
        db.commit()
        db.refresh(db_item)
    return db_item

def delete_fridge_item(db: Session, user_id: int, item_id:int):
    """Delete an item from the User's fridge"""
    db_item = db.query(models.FridgeItem).filter(models.FridgeItem.id == item_id, models.FridgeItem.user_id == user_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item is not None
