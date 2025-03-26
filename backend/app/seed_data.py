from sqlalchemy.orm import Session
from . import models
from .database import engine, SessionLocal

def seed_diets(db: Session):
    """Seed dietary preferences"""
    diets = [
        {"name": "Vegetarian"},
        {"name": "Vegan"},
        {"name": "High-Protein"},
        {"name": "Low-Carb"},
        {"name": "Gluten-Free"},
        {"name": "Dairy-Free"},
    ]
    
    for diet_data in diets:
        diet = db.query(models.Diet).filter(models.Diet.name == diet_data["name"]).first()
        if not diet:
            db.add(models.Diet(**diet_data))
    
    db.commit()

def seed_ingredients(db: Session):
    """Seed basic ingredients"""
    ingredients = [
        # Proteins
        {"name": "Chicken Breast"},
        {"name": "Ground Beef"},
        {"name": "Salmon"},
        {"name": "Tofu"},
        {"name": "Eggs"},
        # Vegetables
        {"name": "Spinach"},
        {"name": "Broccoli"},
        {"name": "Bell Pepper"},
        {"name": "Onion"},
        {"name": "Carrot"},
        {"name": "Tomato"},
        {"name": "Garlic"},
        # Fruits
        {"name": "Apple"},
        {"name": "Banana"},
        {"name": "Strawberry"},
        {"name": "Avocado"},
        # Grains/Starches
        {"name": "Rice"},
        {"name": "Pasta"},
        {"name": "Bread"},
        {"name": "Quinoa"},
        {"name": "Potato"},
        # Dairy
        {"name": "Milk"},
        {"name": "Cheese"},
        {"name": "Yogurt"},
        {"name": "Butter"},
        # Pantry items
        {"name": "Olive Oil"},
        {"name": "Salt"},
        {"name": "Pepper"},
        {"name": "Flour"},
        {"name": "Sugar"},
    ]
    
    db_ingredients = {}
    for ingredient_data in ingredients:
        ingredient = db.query(models.Ingredient).filter(models.Ingredient.name == ingredient_data["name"]).first()
        if not ingredient:
            ingredient = models.Ingredient(**ingredient_data)
            db.add(ingredient)
            db.flush()  # Get ID without committing transaction
        db_ingredients[ingredient.name] = ingredient
    
    db.commit()
    return db_ingredients

def seed_recipes(db: Session, ingredients):
    """Seed initial recipes"""
    # Get diet preferences
    vegetarian = db.query(models.Diet).filter(models.Diet.name == "Vegetarian").first()
    vegan = db.query(models.Diet).filter(models.Diet.name == "Vegan").first()
    high_protein = db.query(models.Diet).filter(models.Diet.name == "High-Protein").first()
    low_carb = db.query(models.Diet).filter(models.Diet.name == "Low-Carb").first()
    
    recipes = [
        {
            "title": "Classic Scrambled Eggs",
            "meal_type": "breakfast",
            "cooking_time": 10,
            "servings": 2,
            "instructions": "1. Crack eggs into a bowl and whisk. 2. Heat butter in a pan over medium heat. 3. Pour eggs into the pan. 4. Stir gently until eggs are set but still moist. 5. Season with salt and pepper.",
            "ingredients": ["Eggs", "Butter", "Salt", "Pepper"],
            "diets": [high_protein, low_carb]
        },
        {
            "title": "Avocado Toast",
            "meal_type": "breakfast",
            "cooking_time": 5,
            "servings": 1,
            "instructions": "1. Toast bread until golden brown. 2. Mash avocado in a bowl. 3. Spread avocado on toast. 4. Season with salt and pepper.",
            "ingredients": ["Bread", "Avocado", "Salt", "Pepper"],
            "diets": [vegetarian, vegan]
        },
        {
            "title": "Chicken Salad",
            "meal_type": "lunch",
            "cooking_time": 15,
            "servings": 2,
            "instructions": "1. Cook chicken breast until done. 2. Chop vegetables. 3. Mix all ingredients in a bowl. 4. Drizzle with olive oil and season.",
            "ingredients": ["Chicken Breast", "Spinach", "Tomato", "Bell Pepper", "Olive Oil", "Salt", "Pepper"],
            "diets": [high_protein, low_carb]
        },
        {
            "title": "Vegetable Stir Fry",
            "meal_type": "dinner",
            "cooking_time": 20,
            "servings": 3,
            "instructions": "1. Heat oil in a pan. 2. Add garlic and onion, cook until fragrant. 3. Add broccoli, bell pepper, and carrot. 4. Stir fry until vegetables are tender-crisp. 5. Season with salt and pepper.",
            "ingredients": ["Broccoli", "Bell Pepper", "Carrot", "Onion", "Garlic", "Olive Oil", "Salt", "Pepper"],
            "diets": [vegetarian, vegan, low_carb]
        },
        {
            "title": "Pasta with Tomato Sauce",
            "meal_type": "dinner",
            "cooking_time": 25,
            "servings": 4,
            "instructions": "1. Cook pasta according to package instructions. 2. Heat olive oil in a pan. 3. Add garlic and onion, cook until fragrant. 4. Add diced tomatoes and simmer for 10 minutes. 5. Combine sauce with pasta.",
            "ingredients": ["Pasta", "Tomato", "Onion", "Garlic", "Olive Oil", "Salt", "Pepper"],
            "diets": [vegetarian, vegan]
        }
    ]
    
    for recipe_data in recipes:
        recipe = db.query(models.Recipe).filter(models.Recipe.title == recipe_data["title"]).first()
        if not recipe:
            # Extract and remove ingredients and diets from data
            ingredient_names = recipe_data.pop("ingredients")
            diet_objects = recipe_data.pop("diets")
            
            # Create recipe
            recipe = models.Recipe(**recipe_data)
            
            # Add ingredients
            for name in ingredient_names:
                if name in ingredients:
                    recipe.ingredients.append(ingredients[name])
            
            # Add diets
            for diet in diet_objects:
                recipe.diets.append(diet)
            
            db.add(recipe)
    
    db.commit()

def main():
    # Create database tables
    models.Base.metadata.create_all(bind=engine)
    
    # Initialize database session
    db = SessionLocal()
    
    try:
        # Seed data
        seed_diets(db)
        ingredients = seed_ingredients(db)
        seed_recipes(db, ingredients)
        
        print("Database seeded successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    main()
