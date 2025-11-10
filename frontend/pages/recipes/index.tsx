import { useState, useEffect, MouseEvent } from "react";
import Link from "next/link";
import { FaFilter, FaHeart, FaTimes } from "react-icons/fa";
import { Diet, Ingredient, MealType } from "../../services/TypeService";
import { Recipe } from "../../services/TypeService";
import MultiSelectAutoComplete, {
  Option,
} from "../../components/MultiSelectAutoComplete";
import {
  getRecipes,
  getAllMealTypes,
  getAllDiets,
  addUserFavouriteRecipe,
} from "../../services/recipeService";
import { getAllIngredients } from "../../services/ingredientService";
import { FiClock, FiUsers } from "react-icons/fi";

export default function Recipes() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [mealTypes, setMealTypes] = useState<MealType[]>([]);
  const [diets, setDiets] = useState<Diet[]>([]);
  const [loading, setLoading] = useState(true);
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
    const fetchRecipesData = async () => {
      setLoading(true);
      try {
        const [recipesData] = await Promise.all([getRecipes(filters)]);

        setRecipes(recipesData);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchRecipesData();
  }, [filters]);

  const handleFilterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const handleIngredientFilterChange = (e: Option[]) => {
    const mappedIngredients = e.map((ingredient) => ({
      id: ingredient.id,
      name: ingredient.label,
    }));

    setFilters((prev) => ({ ...prev, ingredients: mappedIngredients }));
  };

  const clearFilters = () => {
    setFilters({
      ingredients: [],
      mealTypes: [],
      diet: "",
    });
  };

  const allIngredients: Option[] = ingredients.map((ingredient) => ({
    id: ingredient.id,
    label: ingredient.name,
  }));

  const removeOption = (selectedOptionId: number) => {
    setFilters((prev) => ({
      ...prev,
      ingredients: prev.ingredients.filter(
        (ingredient) => ingredient.id !== selectedOptionId
      ),
    }));
  };

  const handleFavouriteClick = async (
    e: MouseEvent<HTMLButtonElement>,
    recipe: Recipe
  ) => {
    e.preventDefault();
    const result = await addUserFavouriteRecipe(recipe.id);
    if (result) {
      setRecipes((prevRecipes) =>
        prevRecipes.map((r) =>
          r.id === recipe.id ? { ...r, isFavourite: true } : r
        )
      );
    }
  };

  return (
    <div className="space-y-6">
      {/* Filter section */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between p-4 bg-white rounded-lg shadow-md">
        <div className="flex flex-wrap gap-2">
          {/* Ingredient filter */}
          <div className="flex items-center">
            <label htmlFor="ingredients" className="mr-2 text-sm font-medium">
              Ingredients:
            </label>
            <MultiSelectAutoComplete
              options={allIngredients}
              selectedOptions={filters.ingredients.map((ingredient) => ({
                id: ingredient.id,
                label: ingredient.name,
              }))}
              onChange={handleIngredientFilterChange}
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
        <div className="flex mt-4 md:mt-0 ms-4">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center px-4 py-2 mr-2 text-sm font-medium text-white bg-blue-600 rounded-md shadow-md hover:bg-blue-700"
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
            <div>
              <div className="card hover:shadow-lg transition-shadow duration-300">
                <div>
                  <Link href={`/recipes/${recipe.id}`}>
                    <img
                      src={recipe.image_url}
                      alt={recipe.title}
                      className="w-full h-48 object-cover"
                    />
                  </Link>

                  <div className="flex justify-between p-4 py-2">
                    <Link href={`/recipes/${recipe.id}`}>
                      <h3 className="text-lg font-medium text-gray-900">
                        {recipe.title}
                      </h3>
                    </Link>

                    <button
                      className="bg-white bg-opacity-75 rounded-full hover:bg-opacity-100"
                      onClick={(e) => handleFavouriteClick(e, recipe)}
                    >
                      {/* TODO This heart adds to favourites but needs to give visual feedback to user (turn to checkmark on successful add) Also needs to maybe start grey then be red for favourites since that makes more sense */}
                      <FaHeart
                        title="Add Recipe to Favourites"
                        className={`text-red-500 ${recipe.isFavourite ? "fill-current" : ""
                          }`}
                      />
                    </button>
                  </div>

                  {(recipe.servings || recipe.cooking_time) && (
                    <div className="flex items-center text-sm text-gray-500 mb-2 ps-4">
                      {recipe.cooking_time && (
                        <div>
                          <FiClock className="mr-1" />
                          <span>{recipe.cooking_time} minutes</span>
                        </div>
                      )}
                      {recipe.cooking_time && recipe.servings && (
                        <span className="mx-2">•</span>
                      )}
                      {recipe.servings && (
                        <div>
                          <FiUsers className="mr-1" />
                          <span>{recipe.servings} servings</span>
                        </div>
                      )}
                    </div>
                  )}
                  <div className="px-3 py-2">
                    {recipe.meal_types &&
                      recipe.meal_types.map((meal_type) => (
                        <span
                          key={meal_type.id}
                          className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 mr-2"
                        >
                          {meal_type.name}
                        </span>
                      ))}
                    {recipe.diets &&
                      recipe.diets.map((diet) => (
                        <span
                          key={diet.id}
                          className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mr-2"
                        >
                          {diet.name}
                        </span>
                      ))}
                  </div>
                  <div className="p-2">
                    <Link
                      href={`/recipes/${recipe.id}`}
                      className="text-primary hover:text-primary-dark font-medium p-2"
                    >
                      View Recipe
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
