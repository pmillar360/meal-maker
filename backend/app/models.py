from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Table
from sqlalchemy.orm import relationship

from .database import Base

# Association table for recipes and ingredients
class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredient"
    recipe_id = Column(Integer, ForeignKey("recipes.id"), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), primary_key=True)
    quantity = Column(String)
    unit = Column(String)

    recipe = relationship("Recipe", back_populates="recipe_ingredients")
    ingredient = relationship("Ingredient", back_populates="ingredient_recipes")

# Association table for recipes and dietary restrictions
recipe_diet = Table(
    "recipe_diet",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id")),
    Column("diet_id", Integer, ForeignKey("diets.id")),
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Relationships
    recipes = relationship("Recipe", back_populates="user")

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    meal_type = Column(String, index=True)  # breakfast, lunch, dinner, snack
    cooking_time = Column(Integer)  # in minutes
    servings = Column(Integer)
    instructions = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    image_url = Column(String)

    # Spoonacular
    spoonacular_id = Column(Integer, unique=True, index=True)
    
    # Relationships
    user = relationship("User", back_populates="recipes")
    recipe_ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    diets = relationship("Diet", secondary=recipe_diet, back_populates="recipes")

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    category = Column(String, index=True)

    spoonacular_id = Column(Integer, unique=True, index=True)
    
    # Relationships
    ingredient_recipes = relationship("RecipeIngredient", back_populates="ingredient", cascade="all, delete-orphan")

class Diet(Base):
    __tablename__ = "diets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    
    # Relationships
    recipes = relationship("Recipe", secondary=recipe_diet, back_populates="diets")

class ShoppingListItem(Base):
    __tablename__ = "shopping_list"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    quantity = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
