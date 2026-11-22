from pydantic import BaseModel, ConfigDict, field_validator
from typing import List, Optional
from datetime import datetime
from util.recipe_normalization import plain_text
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
    aliases: list[str] = []
    id: int

    model_config = ConfigDict(from_attributes=True)

class RecipeIngredientBase(BaseModel):
    quantity: Optional[str] = None
    unit: Optional[str] = None

class RecipeIngredient(RecipeIngredientBase):
    ingredient: Ingredient
    id: int
    original: Optional[str] = None
    preparation: Optional[str] = None
    amount: str

    model_config = ConfigDict(from_attributes=True)

class InstructionSection(BaseModel):
    name: str
    steps: list[str]

class RecipeBase(BaseModel):
    cooking_time: Optional[int] = None
    servings: Optional[int] = None
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
    instruction_sections: list[InstructionSection] = []
    provider: Optional[str] = None
    source_url: Optional[str] = None
    description: Optional[str] = None

    @field_validator("description")
    @classmethod
    def readable_description(cls, value):
        return plain_text(value) if value and "<" in value else value

    model_config = ConfigDict(from_attributes=True)

class RecipeIngredientAvailability(BaseModel):
    ingredient: Ingredient
    quantity: Optional[str] = None
    unit: Optional[str] = None
    has_in_fridge: bool
    missing: bool

    model_config = ConfigDict(from_attributes=True)

class RecipeAvailabilitySummary(BaseModel):
    recipe: Recipe
    total_ingredients: int
    available_ingredients: int
    missing_ingredients: int
    missing_ingredient_names: List[str] = []

class RecipeAvailabilityDetail(BaseModel):
    recipe: RecipeDetail
    ingredient_statuses: List[RecipeIngredientAvailability] = []
    total_ingredients: int
    available_ingredients: int
    missing_ingredients: int
    missing_ingredient_names: List[str] = []

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

class MissingIngredientsAddedResponse(BaseModel):
    created_items: List[ShoppingListItem] = []
    created_count: int

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
    ingredient_id: int | None = None
    name: str
    quantity: Optional[str] = None

class FridgeItemCreate(FridgeItemBase):
    pass

class FridgeItem(FridgeItemBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class FridgeItemUpdate(BaseModel):
    name: str | None = None
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