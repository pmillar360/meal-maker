from fastapi import FastAPI, HTTPException, Depends, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

from crud.users import get_current_active_user
from crud import ingredients
from crud import recipes
from crud import shopping_list
from crud import fridge
from crud import users

from util.auth import (
    oauth2_scheme,
)

from . import models, schemas
from .database import engine, get_db

from util.logger import intialize_logger, get_logger

# Initialize logging
intialize_logger()

logger = get_logger()

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Meal Maker API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # In production, replace with actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return recipes.get_recipes(db, ingredient_list, meal_type, diet, skip, limit)

@app.get("/recipes/{recipe_id}", response_model=schemas.RecipeDetail)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Get detailed information for a specific recipe"""

    return recipes.get_recipe_by_id(db, recipe_id)

# TODO Need to put a hard limit to prevent people from manually requesting large amounts
@app.get("/recipes/featured/", response_model=List[schemas.RecipeDetail])
def get_featured_recipes(
    number: int = 3, # NOTE Not 100% sure if exposing this is needed but it's fine for now
    db: Session = Depends(get_db),
):
    """Get a number of featured recipes"""
    return recipes.get_featured_recipes(db, number=number)

@app.get("/ingredients/", response_model=List[schemas.Ingredient])
def get_all_ingredients(db: Session = Depends(get_db)):
    """Get all available ingredients"""
    return ingredients.get_all_ingredients(db)

@app.get("/diets/", response_model=List[schemas.Diet])
def get_all_diets(db: Session = Depends(get_db)):
    """Get all diets"""
    return recipes.get_all_diets(db)

@app.get("/meal-types/", response_model=List[schemas.MealType])
def get_all_meal_types(db: Session = Depends(get_db)):
    """Get all meal types"""
    return recipes.get_all_meal_types(db)

# Shopping List Endpoints
@app.post("/shopping-list/", response_model=schemas.ShoppingListItem)
def create_shopping_list_item(item: schemas.ShoppingListItemCreate, db: Session = Depends(get_db), user = Depends(get_current_active_user)):
    """Add item to shopping list"""
    return shopping_list.add_shopping_list_item(db, user.id, item)

@app.get("/shopping-list/", response_model=List[schemas.ShoppingListItem])
def read_shopping_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user = Depends(get_current_active_user)):
    """Get all shopping list items"""
    return shopping_list.get_shopping_list(db, user.id, skip, limit)

@app.patch("/shopping-list/{item_id}", response_model=schemas.ShoppingListItem)
def update_shopping_list_item(item_id: int, item: schemas.ShoppingListItemUpdate, db: Session = Depends(get_db), user = Depends(get_current_active_user)):
    """Update shopping list item"""
    db_item = shopping_list.update_shopping_list_item(db, user.id, item_id, item)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.delete("/shopping-list/{item_id}", response_model=bool)
def delete_shopping_list_item(item_id: int, db: Session = Depends(get_db), user = Depends(get_current_active_user)):
    """Delete shopping list item"""
    result = shopping_list.delete_shopping_list_item(db, user.id, item_id)
    if not result:
        raise HTTPException(status_code=404, detail="Item not found")
    return True

@app.post("/token")
def login(
    form_data: schemas.LoginRequest,
    db: Session = Depends(get_db)):
    """Log in a user and return access and refresh tokens"""
    return users.login(form_data, db)

@app.get("/me")
def read_users_me(token: str = Depends(oauth2_scheme)):
    """Checks if token is valid, returns user if so """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    return users.get_current_user_by_token(token)

@app.post("/register")
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Checks if username exists and if not, create the user account and return the access token"""
    return users.register_user(user_data, db)

@app.post("/refresh")
def refresh_token(request: Request):
    # request.cookies
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        # TODO What to do if there is no refresh token? Return nothing? Raise error
        # If 401 is raised here it will get called again because of the interceptor? Shouldn't worry about that
        return None

    return users.refresh_token(refresh_token)

@app.post("/logout")
def logout_user(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}

# Fridge Endpoints
@app.post("/fridge/", response_model=schemas.FridgeItem)
def add_fridge_item(item: schemas.FridgeItemCreate, db: Session = Depends(get_db), user: schemas.User = Depends(get_current_active_user)):
    """Add item to fridge"""
    return fridge.add_fridge_item(db, user.id, item)

@app.get("/fridge/", response_model=List[schemas.FridgeItem])
def get_fridge_items(db: Session = Depends(get_db), user: schemas.User = Depends(get_current_active_user)):
    """Get all of a user's fridge items"""
    return fridge.get_fridge_items(db, user.id)

@app.patch("/fridge/{item_id}", response_model=schemas.FridgeItem)
def update_fridge_item(item_id: int, item: schemas.FridgeItemUpdate, db: Session = Depends(get_db), user: schemas.User = Depends(get_current_active_user)):
    """Update fridge item"""
    db_item = fridge.update_fridge_item(db, user.id, item_id, item)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.delete("/fridge/{item_id}", response_model=bool)
def delete_fridge_item(item_id: int, db: Session = Depends(get_db), user: schemas.User = Depends(get_current_active_user)):
    """Delete fridge item"""
    result = fridge.delete_fridge_item(db, user.id, item_id)
    if not result:
        raise HTTPException(status_code=404, detail="Item not found")
    return True