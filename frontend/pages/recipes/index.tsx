import { useState, useEffect, useMemo } from "react";
import { useRouter } from "next/router";
import { FaFilter, FaSearch, FaTimes } from "react-icons/fa";
import { Diet, Ingredient, MealType } from "../../services/TypeService";
import { Recipe, RecipeAvailabilitySummary } from "../../services/TypeService";
import MultiSelectAutoComplete from "../../components/MultiSelectAutoComplete";
import IngredientMultiSelect from "../../components/IngredientMultiSelect";
import {
  getRecipes,
  getRecipesWithFridgeAvailability,
  getAllMealTypes,
  getAllDiets,
} from "../../services/recipeService";
import { getAllIngredients } from "../../services/ingredientService";
import { rankRecipeAvailability, RecipeRankingMode } from "../../services/recipeRankingService";
import RecipeCard from "../../components/RecipeCard";
import { useAuth } from "../../context/AuthContext";
import { getFridgeIngredients } from "../../services/fridgeService";

const RECIPES_RANKING_MODE: RecipeRankingMode = "balanced";
const GUEST_FRIDGE_STORAGE_KEY = "meal-maker-local-fridge-items";

export default function Recipes() {
  const router = useRouter();
  const { isLoggedIn } = useAuth();
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [availabilityByRecipeId, setAvailabilityByRecipeId] = useState<Record<number, RecipeAvailabilitySummary>>({});
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [fridgeIngredientNames, setFridgeIngredientNames] = useState<string[]>([]);
  const [mealTypes, setMealTypes] = useState<MealType[]>([]);
  const [diets, setDiets] = useState<Diet[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchInput, setSearchInput] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [applyFridgeIngredients, setApplyFridgeIngredients] = useState(false);
  const [initializedApplyFromQuery, setInitializedApplyFromQuery] = useState(false);
  const [filters, setFilters] = useState<Filters>({
    ingredients: [],
    mealTypes: [],
    diet: "",
  });
  const [showFilters, setShowFilters] = useState(true);

  type Filters = {
    ingredients: Ingredient[];
    mealTypes: MealType[];
    diet: string;
  };

  useEffect(() => {
    const timeout = setTimeout(() => {
      setDebouncedSearch(searchInput.trim());
    }, 300);

    return () => clearTimeout(timeout);
  }, [searchInput]);

  useEffect(() => {
    if (!router.isReady || initializedApplyFromQuery) {
      return;
    }

    const applyFridgeValue = router.query.applyFridge;
    const shouldApplyFromQuery =
      applyFridgeValue === "1" ||
      applyFridgeValue === "true" ||
      (Array.isArray(applyFridgeValue) && applyFridgeValue.includes("1"));

    if (shouldApplyFromQuery) {
      setApplyFridgeIngredients(true);
    }

    setInitializedApplyFromQuery(true);
  }, [router.isReady, router.query.applyFridge, initializedApplyFromQuery]);

  // Need to ensure the ingredients, mealtypes, diets are loaded first, then recipes and filter changes
  useEffect(() => {
    // Initial data fetch without filters
    const fetchInitialData = async () => {
      setLoading(true);
      try {
        const [ingredientsData, mealTypesData, dietsData] = await Promise.all([
          getAllIngredients(),
          getAllMealTypes(),
          getAllDiets(),
        ]);

        setIngredients(ingredientsData);
        setMealTypes(mealTypesData);
        setDiets(dietsData);
      } catch (error) {
        console.error("Error fetching initial data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchInitialData();
  }, []);

  useEffect(() => {
    const loadFridgeIngredientNames = async () => {
      if (isLoggedIn) {
        try {
          const fridgeItems = await getFridgeIngredients();
          setFridgeIngredientNames(
            fridgeItems
              .map((item) => item.name.trim())
              .filter((name) => Boolean(name))
          );
        } catch (error) {
          console.error("Error fetching fridge ingredient names:", error);
          setFridgeIngredientNames([]);
        }
        return;
      }

      const stored = localStorage.getItem(GUEST_FRIDGE_STORAGE_KEY);
      if (!stored) {
        setFridgeIngredientNames([]);
        return;
      }

      try {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed)) {
          setFridgeIngredientNames(
            parsed
              .map((item) => String(item).trim())
              .filter((name) => Boolean(name))
          );
          return;
        }
      } catch (error) {
        console.error("Error reading local fridge ingredient names:", error);
      }

      setFridgeIngredientNames([]);
    };

    loadFridgeIngredientNames();
  }, [isLoggedIn]);

  const selectedIngredientFilters = useMemo(() => {
    const dedupedByName = new Map<string, Ingredient>();

    filters.ingredients.forEach((ingredient) => {
      const key = ingredient.name.trim().toLowerCase();
      if (!key) return;
      dedupedByName.set(key, ingredient);
    });

    return Array.from(dedupedByName.values());
  }, [filters.ingredients]);

  const normalizedFridgeIngredientNames = useMemo(
    () => new Set(fridgeIngredientNames.map((name) => name.trim().toLowerCase()).filter(Boolean)),
    [fridgeIngredientNames]
  );

  const queryFilters = useMemo(
    () => ({
      ingredients: selectedIngredientFilters,
      mealTypes: filters.mealTypes,
      diet: filters.diet,
      search: debouncedSearch,
    }),
    [selectedIngredientFilters, filters.mealTypes, filters.diet, debouncedSearch]
  );

  const normalizedSearch = debouncedSearch.toLowerCase();

  useEffect(() => {
    const fetchRecipesData = async () => {
      setLoading(true);
      try {
        if (isLoggedIn) {
          const availabilityData = await getRecipesWithFridgeAvailability(queryFilters);
          const nameFilteredAvailabilityData = normalizedSearch
            ? availabilityData.filter((item) =>
                item.recipe.title.toLowerCase().includes(normalizedSearch)
              )
            : availabilityData;

          const rankedAvailabilityData = rankRecipeAvailability(
            nameFilteredAvailabilityData,
            RECIPES_RANKING_MODE
          );
          const fridgeFilteredAvailabilityData =
            applyFridgeIngredients && fridgeIngredientNames.length > 0
              ? rankedAvailabilityData.filter((item) => item.available_ingredients > 0)
              : rankedAvailabilityData;

          setRecipes(fridgeFilteredAvailabilityData.map((item) => item.recipe));
          const nextAvailabilityMap: Record<number, RecipeAvailabilitySummary> = {};
          fridgeFilteredAvailabilityData.forEach((item) => {
            nextAvailabilityMap[item.recipe.id] = item;
          });
          setAvailabilityByRecipeId(nextAvailabilityMap);
        } else {
          const recipesData = await getRecipes(queryFilters);
          const nameFilteredRecipes = normalizedSearch
            ? recipesData.filter((recipe) =>
                recipe.title.toLowerCase().includes(normalizedSearch)
              )
            : recipesData;

          const fridgeFilteredRecipes =
            applyFridgeIngredients && normalizedFridgeIngredientNames.size > 0
              ? nameFilteredRecipes.filter((recipe) =>
                  (recipe.recipe_ingredients || []).some((recipeIngredient) =>
                    normalizedFridgeIngredientNames.has(
                      recipeIngredient.ingredient.name.trim().toLowerCase()
                    )
                  )
                )
              : nameFilteredRecipes;

          setRecipes(fridgeFilteredRecipes);
          setAvailabilityByRecipeId({});
        }
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchRecipesData();
  }, [
    queryFilters,
    isLoggedIn,
    applyFridgeIngredients,
    fridgeIngredientNames.length,
    normalizedFridgeIngredientNames,
    normalizedSearch,
  ]);

  const handleFilterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const clearFilters = () => {
    setFilters({
      ingredients: [],
      mealTypes: [],
      diet: "",
    });
    setSearchInput("");
    setApplyFridgeIngredients(false);
  };

  const removeOption = (selectedOptionId: number) => {
    setFilters((prev) => ({
      ...prev,
      ingredients: prev.ingredients.filter(
        (ingredient) => ingredient.id !== selectedOptionId
      ),
    }));
  };

  return (
    <div className="space-y-6">
      {/* Filter section */}
      <div className="p-4 bg-white rounded-lg shadow-md space-y-4">
        <div className="space-y-2">
          <label htmlFor="recipe-name-search" className="text-sm font-medium text-gray-700">
            Search Recipes by Name
          </label>
          <div className="relative">
            <FaSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
            <input
              id="recipe-name-search"
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
              placeholder="Try chicken curry, pasta bake, veggie tacos..."
              className="form-input w-full pl-10 pr-12 py-3 text-base"
            />
            {searchInput && (
              <button
                type="button"
                onClick={() => setSearchInput("")}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-gray-500 hover:text-gray-700"
              >
                Clear
              </button>
            )}
          </div>
        </div>

        <div className="flex flex-col gap-2 rounded-lg border border-gray-200 bg-gray-50 p-3">
          <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
            <input
              type="checkbox"
              checked={applyFridgeIngredients}
              onChange={(event) => setApplyFridgeIngredients(event.target.checked)}
              className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
            />
            Apply fridge ingredients
          </label>
          <p className="text-xs text-gray-600">
            {isLoggedIn
              ? "Using your saved fridge ingredients for filtering."
              : "Using local fridge ingredients from this browser."}
          </p>
          {!isLoggedIn && fridgeIngredientNames.length === 0 && (
            <p className="text-xs text-amber-700">
              No local fridge items found yet. Add ingredients on the home page to use this filter.
            </p>
          )}
        </div>

        <div className="flex flex-wrap gap-2">
          {/* Ingredient filter */}
          <div className="flex items-center">
            <label htmlFor="ingredients" className="mr-2 text-sm font-medium">
              Ingredients:
            </label>
            <IngredientMultiSelect
              options={ingredients}
              selectedIngredients={filters.ingredients}
              onChange={(selected) =>
                setFilters((prev) => ({ ...prev, ingredients: selected }))
              }
            />
          </div>

          {/* Meal type filter */}
          <div className="flex items-center text-nowrap">
            <label htmlFor="mealType" className="mr-2 text-sm font-medium">
              Meal Type:
            </label>
            <MultiSelectAutoComplete
              options={mealTypes.map((type) => ({
                id: type.id,
                label: type.name,
              }))}
              selectedOptions={filters.mealTypes.map((type) => ({
                id: type.id,
                label: type.name,
              }))}
              onChange={(selected) =>
                setFilters((prev) => ({
                  ...prev,
                  mealTypes: selected.map(opt => ({ id: opt.id, name: opt.label }))
                }))
              }
            />
          </div>

          {/* Diet type filter */}
          <div className="flex items-center text-nowrap">
            <label htmlFor="diet" className="mr-2 text-sm font-medium">
              Diet Type:
            </label>
            <select
              id="diet"
              name="diet"
              value={filters.diet}
              onChange={handleFilterChange}
              className="p-2 border rounded-md text-sm form-input"
            >
              <option value="">All Diets</option>
              {diets.map((diet) => (
                <option key={diet.id} value={diet.name}>
                  {diet.name.charAt(0).toUpperCase() + diet.name.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Filter and clear buttons */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md shadow-md hover:bg-blue-700"
          >
            <FaFilter className="mr-2" />
            {showFilters ? "Hide Filters" : "Show Filters"}
          </button>
          <button
            onClick={clearFilters}
            className="flex items-center px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md shadow-md hover:bg-red-700"
          >
            <FaTimes className="mr-2" />
            Clear Filters
          </button>
        </div>
      </div>

      {/* Filter chips */}
      <div className="flex flex-wrap gap-2 mb-2">
        {applyFridgeIngredients && (
          <span className="bg-amber-100 text-amber-800 px-2 py-1 rounded-sm flex items-center">
            Fridge Applied ({fridgeIngredientNames.length})
          </span>
        )}
        {debouncedSearch && (
          <span className="bg-slate-100 text-slate-700 px-2 py-1 rounded-sm flex items-center">
            Search: {debouncedSearch}
          </span>
        )}
        {showFilters && filters.mealTypes.map((opt) => (
          <span
            key={opt.id} className="bg-green-100 text-green-700 px-2 py-1 rounded-sm flex items-center">
            {opt.name}
            <button className="ml-1 text-red-500 hover:text-red-700"
              onClick={() => setFilters((prev) => ({
                ...prev,
                mealTypes: prev.mealTypes.filter((mt) => mt.id !== opt.id),
              }))}
            >
              ✕
            </button>
          </span>
        ))}
        {showFilters &&
          filters.ingredients.map((opt) => (
            <span
              key={opt.id}
              className="bg-blue-100 text-blue-700 px-2 py-1 rounded-sm flex items-center"
            >
              {opt.name}
              <button
                onClick={() => removeOption(opt.id)}
                className="ml-1 text-red-500 hover:text-red-700"
              >
                ✕
              </button>
            </span>
          ))}
      </div>

      {/* Recipe list */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {loading ? (
          <div className="col-span-full text-center py-10">
            <p className="text-lg text-gray-500">Loading recipes...</p>
          </div>
        ) : recipes.length === 0 ? (
          <div className="col-span-full text-center py-10">
            <p className="text-lg text-gray-500">No recipes found.</p>
          </div>
        ) : (
          recipes.map((recipe) => (
            <RecipeCard
              key={recipe.id}
              recipe={recipe}
              availability={availabilityByRecipeId[recipe.id]}
            />
          ))
        )}
      </div>
    </div>
  );
}
