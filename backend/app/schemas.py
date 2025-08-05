from pydantic import BaseModel
from typing import List, Optional

# Base schemas
class DietBase(BaseModel):
    name: str

class Diet(DietBase):
    id: int
    
    class Config:
        from_attributes = True

class IngredientBase(BaseModel):
    name: str
    category: Optional[str] = None

class Ingredient(IngredientBase):
    id: int
    
    class Config:
        from_attributes = True

class RecipeBase(BaseModel):
    title: str
    meal_type: Optional[str] = None
    cooking_time: Optional[int] = None
    servings: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

class Recipe(RecipeBase):
    id: int
    
    class Config:
        from_attributes = True

class RecipeDetail(RecipeBase):
    id: int
    instructions: Optional[str] = None
    ingredients: List[Ingredient] = []
    diets: List[Diet] = []
    
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
