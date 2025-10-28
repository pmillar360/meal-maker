from fastapi import FastAPI, HTTPException, Depends, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional

from util.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_refresh_token_age,
)

from . import models, schemas, crud
from .database import engine, get_db
from util.spoonacular import get_external_recipe_by_id

from util.logger import intialize_logger, get_logger

import datetime

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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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
    old_date = datetime.datetime.now() - datetime.timedelta(days=30)

    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    if recipe.last_updated is None or recipe.last_updated < old_date and recipe.spoonacular_id is not None:
        logger.info(f"Making external API request for spooancular ID: {recipe.spoonacular_id}")
        external_data = get_external_recipe_by_id(recipe.spoonacular_id)

        # If recipe cannot be found via API return not found
        if external_data is None:
            raise HTTPException(status_code=404, detail="Recipe not found")

        return crud.create_local_recipe_from_spoonacular(db, external_data)
    
    # Return the local recipe if it exists and was updated within the last 30 days
    return recipe

# TODO Need to put a hard limit to prevent people from manually requesting large amounts
@app.get("/recipes/featured/", response_model=List[schemas.RecipeDetail])
def get_featured_recipes(
    number: int = 3, # NOTE Not 100% sure if exposing this is needed but it's fine for now
    db: Session = Depends(get_db),
):
    """Get a number of featured recipes"""
    return crud.get_featured_recipes(db, number=number)

@app.get("/ingredients/", response_model=List[schemas.Ingredient])
def get_all_ingredients(db: Session = Depends(get_db)):
    """Get all available ingredients"""
    return crud.get_all_ingredients(db)

@app.get("/diets/", response_model=List[schemas.Diet])
def get_all_diets(db: Session = Depends(get_db)):
    """Get all diets"""
    return crud.get_all_diets(db)

@app.get("/meal-types/", response_model=List[schemas.MealType])
def get_all_meal_types(db: Session = Depends(get_db)):
    """Get all meal types"""
    return crud.get_all_meal_types(db)

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

@app.post("/token")
def login(
    form_data: schemas.LoginRequest,
    db: Session = Depends(get_db)):
    """Log in a user and return access and refresh tokens"""
    user = db.query(models.User).filter(models.User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, str(user.hashed_password)):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    token_data = {"sub": user.username}

    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)

    response = JSONResponse({"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=get_refresh_token_age() * 24 * 60 * 60,  # TODO Need to get value from auth.py
    )

    return response

@app.get("/me")
def read_users_me(access_token: str = Depends(oauth2_scheme)):
    """Checks if token is valid, returns user if so """
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    payload = verify_token(access_token) # BUG For some reason this verify fails on the access token
    
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    
    return {"username": payload["sub"]}

@app.post("/register")
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    
    hashed_pwd = hash_password(user_data.password)
    new_user = models.User(username=user_data.username, hashed_password=hashed_pwd)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token({"sub": new_user.username})
    refresh_token = create_refresh_token({"sub": new_user.username})

    response = JSONResponse({"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=get_refresh_token_age() * 24 * 60 * 60,  # TODO Need to get value from auth.py
    )

    return response

@app.post("/refresh")
def refresh_token(request: Request):
    # request.cookies
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        # TODO What to do if there is no refresh token? Return nothing? Raise error
        # If 401 is raised here it will get called again because of the interceptor? Shouldn't worry about that
        return None

    payload = verify_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    new_access_token = create_access_token({"sub": username})
    new_refresh_token = create_refresh_token({"sub": username})
    
    response = JSONResponse({
        "access_token": new_access_token,
        "token_type": "bearer"
    })

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=get_refresh_token_age() * 24 * 60 * 60,  # TODO Need to get value from auth.py
    )
    
    return response

@app.post("/logout")
def logout_user(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}