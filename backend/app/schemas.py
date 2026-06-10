from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
# Schemas are for frontend <-> backend communication

class DietBase(BaseModel):
    name: str

class Diet(DietBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class MealTypeBase(BaseModel):
    name: str

class MealType(MealTypeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class IngredientBase(BaseModel):
    name: str
    category: Optional[str] = None

class Ingredient(IngredientBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class RecipeIngredientBase(BaseModel):
    quantity: Optional[str] = None
    unit: Optional[str] = None

class RecipeIngredient(RecipeIngredientBase):
    ingredient: Ingredient

    model_config = ConfigDict(from_attributes=True)

class RecipeBase(BaseModel):
    title: str
    meal_types: Optional[List[MealType]] = []
    diets: Optional[List[Diet]] = []
    image_url: Optional[str] = None
    is_featured: Optional[bool] = None
    last_updated: Optional[datetime] = None

class Recipe(RecipeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class RecipeDetail(RecipeBase):
    id: int
    instructions: Optional[str] = None
    recipe_ingredients: List[RecipeIngredient] = []
    cooking_time: Optional[int] = None
    servings: Optional[int] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ShoppingListItemBase(BaseModel):
    name: str
    quantity: Optional[str] = None
    category: Optional[str] = None

class ShoppingListItemCreate(ShoppingListItemBase):
    pass

class ShoppingListItem(ShoppingListItemBase):
    id: int
    completed: bool

    model_config = ConfigDict(from_attributes=True)

class ShoppingListItemUpdate(BaseModel):
    quantity: Optional[str] = None
    completed: Optional[bool] = None

class UserCreate(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserIdentity(BaseModel):
    username: str

class FridgeItemBase(BaseModel):
    name: str
    quantity: Optional[str] = None

class FridgeItemCreate(FridgeItemBase):
    pass

class FridgeItem(FridgeItemBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class FridgeItemUpdate(BaseModel):
    quantity: Optional[str] = None

class UserBase(BaseModel):
    username: str

class User(UserBase):
    id: int
    # recipes: List[Recipe] = []
    favourite_recipes: List[Recipe] = []
    shopping_list_items: List[ShoppingListItem] = []
    fridge_items: List[FridgeItem] = []

    model_config = ConfigDict(from_attributes=True)

class FavouriteRecipe(BaseModel):
    user_id: int
    recipe_id: int

    model_config = ConfigDict(from_attributes=True)