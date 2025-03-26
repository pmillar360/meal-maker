from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Table
from sqlalchemy.orm import relationship

from .database import Base

# Association table for recipes and ingredients
recipe_ingredient = Table(
    "recipe_ingredient",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id")),
    Column("ingredient_id", Integer, ForeignKey("ingredients.id")),
)

# Association table for recipes and dietary restrictions
recipe_diet = Table(
    "recipe_diet",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id")),
    Column("diet_id", Integer, ForeignKey("diets.id")),
)

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    meal_type = Column(String, index=True)  # breakfast, lunch, dinner, snack
    cooking_time = Column(Integer)  # in minutes
    servings = Column(Integer)
    instructions = Column(Text)
    
    # Relationships
    ingredients = relationship("Ingredient", secondary=recipe_ingredient, back_populates="recipes")
    diets = relationship("Diet", secondary=recipe_diet, back_populates="recipes")

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    
    # Relationships
    recipes = relationship("Recipe", secondary=recipe_ingredient, back_populates="ingredients")

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
