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
    meal_types: Optional[str] = Query(None, description="Comma separated list of meal types (breakfast, lunch, dinner, snack)"),
    diet: Optional[str] = Query(None, description="Dietary restriction (vegetarian, vegan, etc)"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get recipes with optional filtering by ingredients, meal type, and dietary restrictions"""
    ingredient_list = ingredients.split(",") if ingredients else []
    meal_type_list = meal_types.split(",") if meal_types else []
    return recipes.get_recipes(db, ingredient_list, meal_type_list, diet, skip, limit)

@app.get("/recipes/{recipe_id}", response_model=schemas.RecipeDetail)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Get detailed information for a specific recipe"""

    return recipes.get_recipe_by_id(db, recipe_id)

@app.get("/recipes/featured/", response_model=List[schemas.RecipeDetail])
def get_featured_recipes(
    number: int = 3, # NOTE Not 100% sure if exposing this is needed but it's fine for now
    db: Session = Depends(get_db),
):
    """Get a number of featured recipes"""
    if number < 1 or number > 20:
        raise HTTPException(status_code=400, detail="Number of featured recipes must be between 1 and 20")
    return recipes.get_featured_recipes(db, number)

@app.get("/recipes/suggestions/", response_model=List[schemas.Recipe])
def get_recipe_suggestions(ingredients: str = Query(...), count: int = 5, db: Session = Depends(get_db)):
    """Get recipe suggestions based on user preferences"""
    ingredient_names = ingredients.split(",") if ingredients else []
    return recipes.get_recipe_suggestions_by_ingredients(db, ingredient_names, count, fetchExternal=True)

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
@app.post("/shopping-list/", response_model=schemas.ShoppingListItem, status_code=status.HTTP_201_CREATED)
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

@app.delete("/shopping-list/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shopping_list_item(item_id: int, db: Session = Depends(get_db), user = Depends(get_current_active_user)):
    """Delete shopping list item"""
    result = shopping_list.delete_shopping_list_item(db, user.id, item_id)
    if not result:
        raise HTTPException(status_code=404, detail="Item not found")
    return None

def _refresh_access_token_from_cookie(request: Request):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")
    return users.refresh_token(refresh_token)

def _clear_auth_cookies(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

@app.post("/auth/tokens", response_model=schemas.TokenResponse)
def create_auth_token(
    form_data: schemas.LoginRequest,
    db: Session = Depends(get_db),
):
    """Create access and refresh tokens for an existing user."""
    return users.login(form_data, db)

@app.get("/users/me", response_model=schemas.UserIdentity)
def read_current_user(user: schemas.User = Depends(get_current_active_user)):
    """Get the authenticated user's identity."""
    return {"username": user.username}

@app.post("/users", response_model=schemas.TokenResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a user account and issue initial auth tokens."""
    return users.register_user(user_data, db)

@app.post("/auth/tokens/refresh", response_model=schemas.TokenResponse)
def refresh_auth_token(request: Request):
    """Issue a new access token and rotate the refresh token cookie."""
    return _refresh_access_token_from_cookie(request)

@app.delete("/auth/tokens/current", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_auth_token(response: Response):
    """Delete auth cookies for the current session."""
    _clear_auth_cookies(response)
    return None

# Fridge Endpoints
@app.post("/fridge/", response_model=schemas.FridgeItem, status_code=status.HTTP_201_CREATED)
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

@app.delete("/fridge/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fridge_item(item_id: int, db: Session = Depends(get_db), user: schemas.User = Depends(get_current_active_user)):
    """Delete fridge item"""
    result = fridge.delete_fridge_item(db, user.id, item_id)
    if not result:
        raise HTTPException(status_code=404, detail="Item not found")
    return None

@app.put("/users/me/favourites/{recipe_id}", response_model=schemas.FavouriteRecipe)
def put_user_favourite_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_active_user),
):
    """Idempotently add a recipe to the authenticated user's favourites."""
    return recipes.add_user_favourite_recipe(db, user.id, recipe_id)

@app.get("/users/me/favourites/", response_model=List[schemas.Recipe])
def get_current_user_favourite_recipes(
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_active_user),
):
    """Get the authenticated user's favourite recipes."""
    return recipes.get_user_favourite_recipes(db, user.id)

@app.delete("/users/me/favourites/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_favourite_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_active_user),
):
    """Remove a recipe from the authenticated user's favourites."""
    result = recipes.remove_user_favourite_recipe(db, user.id, recipe_id)
    if not result:
        raise HTTPException(status_code=404, detail="Recipe not found in favourites")
    return None