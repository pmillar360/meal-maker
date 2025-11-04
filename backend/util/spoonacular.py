import os
import requests
from util.logger import log

SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")
BASE_URL = "https://api.spoonacular.com"

# Spoonacular gives 50 points/day then no more calls

# Calling this endpoint requires 1 point and 0.01 points per result returned
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

    log(f"Searching Spoonacular recipes with query: {query} and ingredients: {ingredients}", level=20)
    response = requests.get(RECIPE_URL, params=params)
    response.raise_for_status()
    return response.json()

# Calling this endpoint requires 1 point and 0.1 points if includeNutrition is true + 1 point if addWinePairing is true and + 0.5 points if addTasteData is true 
def get_external_recipe_by_id(id: int):
    RECIPE_URL = BASE_URL + f"/recipes/{id}/information"
    params = {
        "apiKey": SPOONACULAR_API_KEY,
        "includeNutrition": False,
        "addWinePairing": False,
        "addTasteData": False,
    }

    log(f"Fetching Spoonacular recipe by ID: {id}", level=20)
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

    log(f"Searching Spoonacular ingredients with query: {query}", level=20)
    response = requests.get(INGREDIENT_URL, params=params)
    response.raise_for_status()
    return response.json()

# Calling this endpoint requires 1 point and 0.01 points per recipe returned and 0.5 points per recipe returned if includeNutrition is set to true
def get_random_recipes(number=3):
    REQ_URL = BASE_URL + "/recipes/random"

    params = {
        "apiKey": SPOONACULAR_API_KEY,
        "includeNutrition": False,
        "number": number,
    }

    log(f"Fetching {number} random Spoonacular recipes", level=20)
    response = requests.get(REQ_URL, params=params)
    response.raise_for_status()

    return response.json()

# Calling this endpoint requires 1 point and 0.01 points per recipe returned
def get_recipes_by_ingredients(ingredients, number=10):
    REQ_URL = BASE_URL + "/recipes/findByIngredients"

    params = {
        "apiKey": SPOONACULAR_API_KEY,
        "ingredients": ",".join(ingredients),
        "number": number,
        "ranking": 1,  # 1 = maximize used ingredients, 2 = minimize missing ingredients
        "ignorePantry": True, # ignore common pantry items like water, salt, flour TODO test the difference and maybe make it an option
    }

    log(f"Fetching Spoonacular recipes by ingredients: {ingredients}", level=20)
    response = requests.get(REQ_URL, params=params)
    response.raise_for_status()

    return response.json()