import os
import requests

SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")
BASE_URL = "https://api.spoonacular.com"

def search_recipes(query=None, ingredients=None, number=10):
    RECIPE_URL = BASE_URL + "/recipes/complexSearch"

    params = {
        "apiKey": SPOONACULAR_API_KEY,
        "number": number,
    }

    if query:
        params["query"] = query
    if ingredients:
        params["includeIngredients"] = ",".join(ingredients)

    response = requests.get(RECIPE_URL, params=params)
    response.raise_for_status()
    return response.json()

def search_ingredients(query=None, number=10):
    INGREDIENT_URL = BASE_URL + "/food/ingredients/search"

    params = {
        "apiKey": SPOONACULAR_API_KEY,
        "number": number,
    }

    if query:
        params["query"] = query

    response = requests.get(INGREDIENT_URL, params=params)
    response.raise_for_status()
    return response.json()