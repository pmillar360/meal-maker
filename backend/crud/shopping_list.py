from collections import defaultdict
from util.recipe_normalization import measurement, format_measure
from sqlalchemy.orm import Session
from app import models, schemas

def add_shopping_list_item(db: Session, user_id: int, item: schemas.ShoppingListItemCreate):
    """Add item to shopping list"""
    db_item = models.ShoppingListItem(**item.model_dump())
    db_item.user_id = user_id
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_shopping_list(db: Session, user_id: int,  skip: int = 0, limit: int = 100):
    """Get all of a user's shopping list items"""
    return db.query(models.ShoppingListItem).filter(models.ShoppingListItem.user_id == user_id).offset(skip).limit(limit).all()

def update_shopping_list_item(db: Session, user_id: int, item_id: int, item_update: schemas.ShoppingListItemUpdate):
    """Update shopping list item status or quantity"""
    db_item = db.query(models.ShoppingListItem).filter(models.ShoppingListItem.id == item_id, models.ShoppingListItem.user_id == user_id).first()
    if db_item:
        update_data = item_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_item, key, value)
        db.commit()
        db.refresh(db_item)
    return db_item

def delete_shopping_list_item(db: Session, user_id:int, item_id: int):
    """Delete shopping list item"""
    db_item = db.query(models.ShoppingListItem).filter(models.ShoppingListItem.id == item_id, models.ShoppingListItem.user_id == user_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
        return True
    return False


def add_recipe_ingredients_to_shopping_list(db: Session, user_id: int, missing_recipe_ingredients: list[models.RecipeIngredient]):
    """Create shopping list items from missing recipe ingredients for a user."""
    created_items = []

    grouped = defaultdict(list)
    for line in missing_recipe_ingredients:
        grouped[line.ingredient_id].append(line)

    for lines in grouped.values():
        recipe_ingredient = lines[0]
        totals = {}
        descriptions = []
        for line in lines:
            parsed = measurement(line.metric_quantity or line.quantity, line.metric_unit or line.unit)
            if parsed and len(parsed[0]) == 1:
                values, unit = parsed
                totals[unit] = totals.get(unit, 0) + values[0]
            elif line.amount:
                descriptions.append(line.amount)
        amounts = [format_measure([total], unit) for unit, total in totals.items()]
        quantity_text = " + ".join(amounts + descriptions) or None

        db_item = models.ShoppingListItem(
            user_id=user_id,
            name=recipe_ingredient.ingredient.name,
            quantity=quantity_text,
            category=recipe_ingredient.ingredient.category,
            completed=False,
        )

        db.add(db_item)
        created_items.append(db_item)

    db.commit()

    for item in created_items:
        db.refresh(item)

    return created_items