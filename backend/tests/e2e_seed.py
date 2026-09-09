"""Create deterministic data for the browser end-to-end suite."""

from pathlib import Path


database_path = Path(__file__).resolve().parents[1] / "e2e_test.db"
database_path.unlink(missing_ok=True)

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models import Diet, Ingredient, MealType, Recipe, RecipeIngredient  # noqa: E402


def add_recipe(
    db,
    *,
    recipe_id: int,
    title: str,
    description: str,
    cooking_time: int,
    servings: int,
    meal_type: MealType,
    diets: list[Diet],
    ingredients: list[tuple[Ingredient, str, str]],
) -> None:
    recipe = Recipe(
        id=recipe_id,
        title=title,
        description=description,
        cooking_time=cooking_time,
        servings=servings,
        instructions="Prepare the ingredients, cook until done, and serve.",
        image_url="https://placehold.co/640x360/png",
        is_featured=True,
    )
    recipe.meal_types.append(meal_type)
    recipe.diets.extend(diets)
    for ingredient, quantity, unit in ingredients:
        recipe.recipe_ingredients.append(
            RecipeIngredient(ingredient=ingredient, quantity=quantity, unit=unit)
        )
    db.add(recipe)


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        breakfast = MealType(name="Breakfast")
        lunch = MealType(name="Lunch")
        dinner = MealType(name="Dinner")
        snack = MealType(name="Snack")
        side = MealType(name="Side")
        vegetarian = Diet(name="Vegetarian")
        vegan = Diet(name="Vegan")
        high_protein = Diet(name="High-Protein")
        tomato = Ingredient(name="Tomato", category="Produce")
        pasta = Ingredient(name="Pasta", category="Pantry")
        egg = Ingredient(name="Egg", category="Dairy")
        chicken = Ingredient(name="Chicken", category="Meat")
        apple = Ingredient(name="Apple", category="Produce")

        db.add_all(
            [
                breakfast,
                lunch,
                dinner,
                snack,
                side,
                vegetarian,
                vegan,
                high_protein,
                tomato,
                pasta,
                egg,
                chicken,
                apple,
            ]
        )

        add_recipe(
            db,
            recipe_id=1,
            title="Tomato Pasta",
            description="A quick tomato pasta.",
            cooking_time=20,
            servings=2,
            meal_type=dinner,
            diets=[vegetarian, vegan],
            ingredients=[(tomato, "2", "whole"), (pasta, "200", "g")],
        )
        add_recipe(
            db,
            recipe_id=2,
            title="Breakfast Omelette",
            description="A protein-rich breakfast.",
            cooking_time=10,
            servings=1,
            meal_type=breakfast,
            diets=[vegetarian, high_protein],
            ingredients=[(egg, "2", "whole"), (tomato, "1", "whole")],
        )
        add_recipe(
            db,
            recipe_id=3,
            title="Chicken Lunch Bowl",
            description="A simple lunch bowl.",
            cooking_time=25,
            servings=2,
            meal_type=lunch,
            diets=[high_protein],
            ingredients=[(chicken, "250", "g"), (tomato, "1", "whole")],
        )
        add_recipe(
            db,
            recipe_id=4,
            title="Apple Snack",
            description="A light vegan snack.",
            cooking_time=5,
            servings=1,
            meal_type=snack,
            diets=[vegan],
            ingredients=[(apple, "1", "whole")],
        )
        add_recipe(
            db,
            recipe_id=5,
            title="Tomato Soup",
            description="A simple tomato side.",
            cooking_time=15,
            servings=2,
            meal_type=side,
            diets=[vegetarian],
            ingredients=[(tomato, "3", "whole")],
        )
        add_recipe(
            db,
            recipe_id=6,
            title="Tomato Salsa",
            description="A fresh tomato side.",
            cooking_time=10,
            servings=4,
            meal_type=side,
            diets=[vegan],
            ingredients=[(tomato, "2", "whole")],
        )
        db.commit()


if __name__ == "__main__":
    main()
