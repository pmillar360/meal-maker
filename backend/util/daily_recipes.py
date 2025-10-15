from datetime import datetime
from util.spoonacular import get_random_recipes
from util.logger import log

CACHE = {}

def get_daily_recipes():
    today = datetime.date
    if CACHE.get("date") != today:
        # Load random recipes
        log(msg="Cache out of date or non-existant -- Loading new recipes")        
        response = get_random_recipes(10)
        CACHE["recipes"] = response["recipes"]  # Extract the recipes array from the response
        CACHE["date"] = today

    return CACHE["recipes"]