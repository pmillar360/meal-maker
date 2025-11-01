from sqlalchemy.orm import Session

from app import models, schemas

def add_fridge_item(db: Session, user_id: int, item: schemas.FridgeItemCreate):
    """Add item to the User's fridge"""
    db_item = models.FridgeItem(**item.model_dump()) # NOTE Verify this works
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
