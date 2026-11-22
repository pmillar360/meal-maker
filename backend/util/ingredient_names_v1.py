"""English catalog naming rules shared with the initial fridge identity migration."""
from functools import lru_cache

import inflect

ALIASES = {"scallion": "green onion", "scallions": "green onion"}


_english = inflect.engine()
_FIXED_NAMES = {"oats", "chives", "preserves", "greens", "hummus", "couscous", "asparagus", "molasses", "watercress"}


@lru_cache(maxsize=4096)
def ingredient_key(name):
    key = " ".join(name.casefold().split())
    key = ALIASES.get(key, key)
    prefix, space, noun = key.rpartition(" ")
    if not noun or noun in _FIXED_NAMES or noun.endswith(("ss", "us", "is")):
        return key
    singular = _english.singular_noun(noun)
    if singular and singular != noun and _english.plural_noun(singular) == noun:
        return prefix + space + singular
    return key


@lru_cache(maxsize=4096)
def ingredient_aliases(key):
    aliases = [alias for alias, target in ALIASES.items() if target == key]
    plural = _english.plural_noun(key)
    if plural and ingredient_key(plural) == key:
        aliases.append(plural)
    return list(dict.fromkeys([*aliases, key]))
