from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Base schemas
class DietBase(BaseModel):
    name: str

class Diet(DietBase):
    id: int
    
    class Config:
        from_attributes = True

class MealTypeBase(BaseModel):
    name: str

class MealType(MealTypeBase):
    id: int

    class Config:
        from_attributes = True

class IngredientBase(BaseModel):
    name: str
    category: Optional[str] = None
    spoonacular_id: Optional[int] = None

class Ingredient(IngredientBase):
    id: int
    
    class Config:
        from_attributes = True

class RecipeIngredientBase(BaseModel):
    quantity: Optional[str] = None
    unit: Optional[str] = None

class RecipeIngredient(RecipeIngredientBase):
    ingredient: Ingredient

    class Config:
        from_attributes = True

class RecipeBase(BaseModel):
    title: str
    meal_types: Optional[List[MealType]] = None
    diets: Optional[List[Diet]] = []
    image_url: Optional[str] = None
    is_featured: Optional[bool] = None
    last_updated: Optional[datetime] = None

class Recipe(RecipeBase):
    id: int
    
    class Config:
        from_attributes = True

class RecipeDetail(RecipeBase):
    id: int
    instructions: Optional[str] = None
    recipe_ingredients: List[RecipeIngredient] = []
    cooking_time: Optional[int] = None
    servings: Optional[int] = None
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

class ShoppingListItemBase(BaseModel):
    name: str
    quantity: Optional[str] = None

class ShoppingListItemCreate(ShoppingListItemBase):
    pass

class ShoppingListItem(ShoppingListItemBase):
    id: int
    completed: bool
    
    class Config:
        from_attributes = True

class ShoppingListItemUpdate(BaseModel):
    quantity: Optional[str] = None
    completed: Optional[bool] = None

class UserCreate(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str
