import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Table, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .database import Base
# Models are for DB <-> Backend communication
# https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html#migrating-an-existing-mapping

# Association table for recipes and ingredients
class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredient"
    recipe_id = mapped_column(Integer, ForeignKey("recipes.id"), primary_key=True)
    ingredient_id = mapped_column(Integer, ForeignKey("ingredients.id"), primary_key=True)
    quantity = mapped_column(String)
    unit = mapped_column(String)

    recipe = relationship("Recipe", back_populates="recipe_ingredients")
    ingredient = relationship("Ingredient", back_populates="ingredient_recipes")

class FavouriteRecipe(Base):
    __tablename__ = "favourite_recipes"
    user_id = mapped_column(ForeignKey("users.id"), primary_key=True)
    recipe_id = mapped_column(ForeignKey("recipes.id"), primary_key=True)

    user = relationship("User", back_populates="favourite_recipes")
    recipe = relationship("Recipe", back_populates="favourited_by")

# Association table for recipes and dietary restrictions
recipe_diet = Table(
    "recipe_diet",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id")),
    Column("diet_id", Integer, ForeignKey("diets.id")),
)

recipe_meal_type = Table(
    "recipe_meal_type",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id")),
    Column("meal_type_id", Integer, ForeignKey("meal_types.id")),
)

class User(Base):
    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True, index=True)
    username = mapped_column(String, unique=True, index=True)
    hashed_password = mapped_column(String)
    is_active = mapped_column(Boolean, default=True)
    is_superuser = mapped_column(Boolean, default=False)
    
    # Relationships
    recipes = relationship("Recipe", back_populates="user")
    favourite_recipes = relationship("FavouriteRecipe", back_populates="user")
    shopping_list_items = relationship("ShoppingListItem", back_populates="user", cascade="all, delete-orphan")
    fridge_items = relationship("FridgeItem", back_populates="user", cascade="all, delete-orphan")

class Recipe(Base):
    __tablename__ = "recipes"

    id = mapped_column(Integer, primary_key=True, index=True)
    title = mapped_column(String, index=True)
    description = mapped_column(Text)
    cooking_time = mapped_column(Integer)  # in minutes
    servings = mapped_column(Integer)
    instructions = mapped_column(Text)
    user_id = mapped_column(Integer, ForeignKey("users.id"))
    image_url = mapped_column(String)
    last_updated: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Spoonacular
    spoonacular_id = mapped_column(Integer, unique=True, index=True)
    
    # Relationships
    user = relationship("User", back_populates="recipes")
    recipe_ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    meal_types = relationship("MealType", secondary=recipe_meal_type, back_populates="recipes")
    diets = relationship("Diet", secondary=recipe_diet, back_populates="recipes")
    favourited_by = relationship("FavouriteRecipe", back_populates="recipe")

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = mapped_column(Integer, primary_key=True, index=True)
    name = mapped_column(String, index=True, unique=True)
    category = mapped_column(String, index=True)

    spoonacular_id = mapped_column(Integer, unique=True, index=True)
    
    # Relationships
    ingredient_recipes = relationship("RecipeIngredient", back_populates="ingredient", cascade="all, delete-orphan")

class Diet(Base):
    __tablename__ = "diets"

    id = mapped_column(Integer, primary_key=True, index=True)
    name = mapped_column(String, index=True, unique=True)
    
    # Relationships
    recipes = relationship("Recipe", secondary=recipe_diet, back_populates="diets")

class ShoppingListItem(Base):
    __tablename__ = "shopping_list_items"

    id = mapped_column(Integer, primary_key=True, index=True)
    user_id = mapped_column(Integer, ForeignKey("users.id"))
    name = mapped_column(String, index=True)
    quantity = mapped_column(String)
    completed = mapped_column(Boolean, default=False)
    category = mapped_column(String, index=True)
    # TODO Attach an ingredient object to this? Probably not needed. Maybe just id?
    
    user = relationship("User", back_populates="shopping_list_items")

class MealType(Base):
    __tablename__ = "meal_types"

    id = mapped_column(Integer, primary_key=True, index=True)
    name = mapped_column(String, index=True, unique=True)

    recipes = relationship("Recipe", secondary=recipe_meal_type, back_populates="meal_types")

class FridgeItem(Base):
    __tablename__ = "fridge_items"
    id = mapped_column(Integer, primary_key=True, index=True)
    user_id = mapped_column(Integer, ForeignKey("users.id"))
    name = mapped_column(String)
    quantity = mapped_column(String)
    # expiry date?

    user = relationship("User", back_populates="fridge_items")