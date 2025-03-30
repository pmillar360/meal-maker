MVP Plan – Meal Maker App
1. Core Features (MVP Scope)
✅ Ingredient-Based Recipe Suggestions

Users input ingredients they have.

The app suggests meal ideas based on those ingredients.

✅ Basic Recipe Database (Preloaded or API)

Start with a small local database (JSON or SQLite) of 50–100 recipes.

Optionally, integrate Spoonacular API or Edamam API for recipes.

✅ Simple Filtering

Users can filter by meal type: Breakfast, Lunch, Dinner, Snacks.

Users can filter by dietary needs: Vegetarian, Vegan, High-Protein, etc.
    - These can be tags for recipes/meals
    - A user can mark themself as vegetarian or vegan to only see those types of meals

User can filter by a specific ingredient they want to be included in the meal

✅ Recipe Detail Page

Ingredients list.

Step-by-step cooking instructions.

Estimated cooking time and servings.

✅ Shopping List Generator

If an ingredient is missing, users can add it to a grocery list.

2. Tech Stack (MVP-Friendly & Scalable)
Frontend:
React (Next.js) – Fast, SEO-friendly, and easy for future expansion.

Tailwind CSS – For a clean, simple UI.

Backend:
FastAPI (Python) – Lightweight and perfect for handling recipe queries.

PostgreSQL – Scalable database for storing recipes and user preferences.

Optional: Firebase – If you want quick authentication and storage.

APIs (Optional for More Recipes)
Spoonacular API (Free tier available) – To fetch recipes dynamically.

Edamam API – For more detailed nutritional analysis.