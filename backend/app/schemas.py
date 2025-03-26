from pydantic import BaseModel
from typing import List, Optional

# Base schemas
class DietBase(BaseModel):
    name: str

class Diet(DietBase):
    id: int
    
    class Config:
        orm_mode = True

class IngredientBase(BaseModel):
    name: str

class Ingredient(IngredientBase):
    id: int
    
    class Config:
        orm_mode = True

class RecipeBase(BaseModel):
    title: str
    meal_type: str
    cooking_time: int
    servings: int

class Recipe(RecipeBase):
    id: int
    
    class Config:
        orm_mode = True

class RecipeDetail(RecipeBase):
    id: int
    instructions: str
    ingredients: List[Ingredient]
    diets: List[Diet]
    
    class Config:
        orm_mode = True

class ShoppingListItemBase(BaseModel):
    name: str
    quantity: Optional[str] = None

class ShoppingListItemCreate(ShoppingListItemBase):
    pass

class ShoppingListItem(ShoppingListItemBase):
    id: int
    completed: bool
    
    class Config:
        orm_mode = True

class ShoppingListItemUpdate(BaseModel):
    quantity: Optional[str] = None
    completed: Optional[bool] = None
