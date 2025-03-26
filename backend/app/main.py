from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os

from . import models, schemas, crud
from .database import engine, SessionLocal

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Meal Maker API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to Meal Maker API"}

@app.get("/recipes/", response_model=List[schemas.Recipe])
def get_recipes(
    ingredients: Optional[str] = Query(None, description="Comma separated list of ingredients"),
    meal_type: Optional[str] = Query(None, description="Meal type (breakfast, lunch, dinner, snack)"),
    diet: Optional[str] = Query(None, description="Dietary restriction (vegetarian, vegan, etc)"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get recipes with optional filtering by ingredients, meal type, and dietary restrictions"""
    ingredient_list = ingredients.split(",") if ingredients else []
    return crud.get_recipes(db, ingredient_list, meal_type, diet, skip, limit)

@app.get("/recipes/{recipe_id}", response_model=schemas.RecipeDetail)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Get detailed information for a specific recipe"""
    recipe = crud.get_recipe(db, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

@app.get("/ingredients/", response_model=List[schemas.Ingredient])
def get_all_ingredients(db: Session = Depends(get_db)):
    """Get all available ingredients"""
    return crud.get_all_ingredients(db)

# Shopping List Endpoints
@app.post("/shopping-list/", response_model=schemas.ShoppingListItem)
def create_shopping_list_item(item: schemas.ShoppingListItemCreate, db: Session = Depends(get_db)):
    """Add item to shopping list"""
    return crud.add_shopping_list_item(db, item)

@app.get("/shopping-list/", response_model=List[schemas.ShoppingListItem])
def read_shopping_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all shopping list items"""
    return crud.get_shopping_list(db, skip, limit)

@app.patch("/shopping-list/{item_id}", response_model=schemas.ShoppingListItem)
def update_shopping_list_item(item_id: int, item: schemas.ShoppingListItemUpdate, db: Session = Depends(get_db)):
    """Update shopping list item"""
    db_item = crud.update_shopping_list_item(db, item_id, item)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.delete("/shopping-list/{item_id}", response_model=bool)
def delete_shopping_list_item(item_id: int, db: Session = Depends(get_db)):
    """Delete shopping list item"""
    result = crud.delete_shopping_list_item(db, item_id)
    if not result:
        raise HTTPException(status_code=404, detail="Item not found")
    return True
