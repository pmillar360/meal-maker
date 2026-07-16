import { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import Link from 'next/link';
import { FridgeItem, Recipe, RecipeAvailabilitySummary } from '../services/TypeService';
import {
  getFeaturedRecipes,
  getRecipeById,
  getRecipesByIngredients,
  getRecipesWithFridgeAvailability,
  getUserFavouriteRecipes,
} from '../services/recipeService';
import RecipeCard from '../components/RecipeCard';
import { useAuth } from '../context/AuthContext';
import { addFridgeIngredient, deleteFridgeIngredient, getFridgeIngredients } from '../services/fridgeService';

export default function Home() {
  const { isLoggedIn } = useAuth();
  const [featuredRecipes, setFeaturedRecipes] = useState<Recipe[]>([]);
  const [fridgeItems, setFridgeItems] = useState<FridgeItem[]>([]);
  const [localFridgeItems, setLocalFridgeItems] = useState<string[]>([]);
  const [fridgeInput, setFridgeInput] = useState('');
  const [matchedRecipes, setMatchedRecipes] = useState<Recipe[]>([]);
  const [availabilityByRecipeId, setAvailabilityByRecipeId] = useState<Record<number, RecipeAvailabilitySummary>>({});
  const [favouriteRecipeIds, setFavouriteRecipeIds] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);
  const [matchingLoading, setMatchingLoading] = useState(false);

  const activeFridgeNames = useMemo(
    () => (isLoggedIn ? fridgeItems.map((item) => item.name) : localFridgeItems),
    [isLoggedIn, fridgeItems, localFridgeItems]
  );

  const loadLoggedInMatches = async () => {
    setMatchingLoading(true);
    try {
      const [fridgeData, availabilityData] = await Promise.all([
        getFridgeIngredients(),
        getRecipesWithFridgeAvailability(),
      ]);

      setFridgeItems(fridgeData);

      const sortedAvailability = [...availabilityData].sort((a, b) => {
        if (a.missing_ingredients !== b.missing_ingredients) {
          return a.missing_ingredients - b.missing_ingredients;
        }
        return b.available_ingredients - a.available_ingredients;
      });

      const topMatches = sortedAvailability.slice(0, 9);
      const nextAvailabilityMap: Record<number, RecipeAvailabilitySummary> = {};
      topMatches.forEach((item) => {
        nextAvailabilityMap[item.recipe.id] = item;
      });

      setMatchedRecipes(topMatches.map((item) => item.recipe));
      setAvailabilityByRecipeId(nextAvailabilityMap);
    } catch (error) {
      console.error('Failed to load fridge-based recipe matches:', error);
    } finally {
      setMatchingLoading(false);
    }
  };

  useEffect(() => {
    const loadFeaturedRecipes = async () => {
      try {
        const recipes = await getFeaturedRecipes(9);
        setFeaturedRecipes(recipes);
        setLoading(false);
      } catch (error) {
        if (axios.isAxiosError(error) && !error.response) {
          // Network error — server is asleep, overlay handles it, keep loading state
        } else {
          console.error("Failed to load featured recipes:", error);
          setLoading(false);
        }
      }
    };
    loadFeaturedRecipes();
  }, []);

  useEffect(() => {
    if (!isLoggedIn) {
      setFridgeItems([]);
      setAvailabilityByRecipeId({});
      return;
    }

    loadLoggedInMatches();
  }, [isLoggedIn]);

  useEffect(() => {
    if (isLoggedIn || localFridgeItems.length === 0) {
      if (!isLoggedIn) {
        setMatchedRecipes([]);
        setAvailabilityByRecipeId({});
      }
      return;
    }

    const loadLocalMatches = async () => {
      setMatchingLoading(true);
      try {
        const recipes = await getRecipesByIngredients(localFridgeItems, 9);
        const recipeDetails = await Promise.all(
          recipes.map((recipe) => getRecipeById(recipe.id).catch(() => null))
        );

        const validDetails = recipeDetails.filter((recipe): recipe is Recipe => Boolean(recipe));
        const fridgeSet = new Set(localFridgeItems.map((name) => name.trim().toLowerCase()));
        const nextAvailabilityMap: Record<number, RecipeAvailabilitySummary> = {};

        validDetails.forEach((recipe) => {
          const total = recipe.recipe_ingredients?.length || 0;
          const available = (recipe.recipe_ingredients || []).filter((item) =>
            fridgeSet.has(item.ingredient.name.trim().toLowerCase())
          ).length;
          const missing = total - available;

          nextAvailabilityMap[recipe.id] = {
            recipe,
            total_ingredients: total,
            available_ingredients: available,
            missing_ingredients: missing,
            missing_ingredient_names: (recipe.recipe_ingredients || [])
              .filter((item) => !fridgeSet.has(item.ingredient.name.trim().toLowerCase()))
              .map((item) => item.ingredient.name),
          };
        });

        setMatchedRecipes(validDetails);
        setAvailabilityByRecipeId(nextAvailabilityMap);
      } catch (error) {
        console.error('Failed to load local fridge matches:', error);
      } finally {
        setMatchingLoading(false);
      }
    };

    loadLocalMatches();
  }, [isLoggedIn, localFridgeItems]);

  useEffect(() => {
    if (isLoggedIn) {
      const loadFavourites = async () => {
        try {
          const favourites = await getUserFavouriteRecipes();
          setFavouriteRecipeIds(favourites.map(f => f.id));
        } catch (error) {
          console.error("Failed to load favourite recipes:", error);
        }
      };
      loadFavourites();
    }
  }, [isLoggedIn]);

  const handleAddFridgeItem = async () => {
    const nextIngredient = fridgeInput.trim();
    if (!nextIngredient) {
      return;
    }

    if (isLoggedIn) {
      try {
        await addFridgeIngredient({ name: nextIngredient, quantity: '' });
        setFridgeInput('');
        await loadLoggedInMatches();
      } catch (error) {
        console.error('Failed to add fridge ingredient:', error);
      }
      return;
    }

    setLocalFridgeItems((prev) => {
      if (prev.some((item) => item.toLowerCase() === nextIngredient.toLowerCase())) {
        return prev;
      }
      return [...prev, nextIngredient];
    });
    setFridgeInput('');
  };

  const handleRemoveFridgeItem = async (value: number | string) => {
    if (isLoggedIn && typeof value === 'number') {
      try {
        await deleteFridgeIngredient(value);
        await loadLoggedInMatches();
      } catch (error) {
        console.error('Failed to remove fridge ingredient:', error);
      }
      return;
    }

    if (typeof value === 'string') {
      setLocalFridgeItems((prev) => prev.filter((item) => item !== value));
    }
  };

  return (
    <div className="space-y-10">
      {/* Hero Section */}
      <section className="rounded-xl bg-linear-to-r from-primary-light to-primary p-8 text-white">
        <div className="max-w-3xl mx-auto text-center space-y-6">
          <h1 className="text-4xl font-bold">Welcome to Meal Maker</h1>
          <p className="text-xl">Add your fridge ingredients and instantly find what you can cook</p>
          <div className="flex justify-center space-x-4">
            <Link href="/recipes" className="btn bg-white text-primary hover:bg-gray-100">
              Browse Recipes
            </Link>
            <Link href="/shopping-list" className="btn bg-primary-dark text-white hover:bg-opacity-90">
              My Shopping List
            </Link>
          </div>
        </div>
      </section>

      <section className="py-2">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold">What Can I Cook Right Now?</h2>
          <Link href="/recipes" className="text-primary hover:text-primary-dark">
            Explore all recipes →
          </Link>
        </div>

        <div className="card p-5 space-y-4">
          <div className="flex flex-col gap-3 sm:flex-row">
            <input
              type="text"
              className="form-input grow"
              value={fridgeInput}
              onChange={(e) => setFridgeInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  handleAddFridgeItem();
                }
              }}
              placeholder="Add an ingredient (e.g. eggs, spinach, onion)"
            />
            <button className="btn btn-primary" onClick={handleAddFridgeItem}>
              Add Ingredient
            </button>
          </div>

          {!isLoggedIn && (
            <p className="text-sm text-gray-500">
              You are using temporary local fridge matching. Log in to save your fridge and sync availability across pages.
            </p>
          )}

          <div className="flex flex-wrap gap-2">
            {isLoggedIn
              ? fridgeItems.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => handleRemoveFridgeItem(item.id)}
                    className="rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-800 hover:bg-blue-200"
                  >
                    {item.name} ×
                  </button>
                ))
              : localFridgeItems.map((item) => (
                  <button
                    key={item}
                    onClick={() => handleRemoveFridgeItem(item)}
                    className="rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-800 hover:bg-blue-200"
                  >
                    {item} ×
                  </button>
                ))}
            {activeFridgeNames.length === 0 && (
              <p className="text-sm text-gray-500">Add ingredients to start getting recipe matches.</p>
            )}
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {matchingLoading ? (
              <p>Finding your best recipe matches...</p>
            ) : matchedRecipes.length > 0 ? (
              matchedRecipes.map((recipe) => (
                <RecipeCard
                  key={recipe.id}
                  recipe={recipe}
                  favouriteRecipeIds={favouriteRecipeIds}
                  availability={availabilityByRecipeId[recipe.id]}
                />
              ))
            ) : (
              <p className="text-gray-500">No recipe matches yet.</p>
            )}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-8">
        <h2 className="text-2xl font-bold text-center mb-8">How It Works</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="card p-6 text-center">
            <div className="text-primary text-4xl mb-4">1</div>
            <h3 className="text-xl font-semibold mb-2">Add Your Fridge</h3>
            <p className="text-gray-600">List what you already have at home</p>
          </div>
          <div className="card p-6 text-center">
            <div className="text-primary text-4xl mb-4">2</div>
            <h3 className="text-xl font-semibold mb-2">See Recipe Availability</h3>
            <p className="text-gray-600">Quickly spot what you can make and what is missing</p>
          </div>
          <div className="card p-6 text-center">
            <div className="text-primary text-4xl mb-4">3</div>
            <h3 className="text-xl font-semibold mb-2">Create Shopping Lists</h3>
            <p className="text-gray-600">Add missing ingredients to your shopping list</p>
          </div>
        </div>
      </section>
      {/* Featured Recipes Section */}
      <section className="py-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Featured Recipes</h2>
          <Link href="/recipes" className="text-primary hover:text-primary-dark">
            View all →
          </Link>
        </div>
        <div className="grid md:grid-cols-3 gap-6">
          {loading ? (
            <p>Loading featured recipes...</p>
          ) : featuredRecipes.length > 0 ? (
            featuredRecipes.map(recipe => (
              <RecipeCard 
                key={recipe.id} 
                recipe={recipe} 
                favouriteRecipeIds={favouriteRecipeIds}
              />
            ))
          ) : (
            <p className="text-gray-500">No featured recipes available</p>
          )}
        </div>
      </section>
    </div>
  );
}
