import { useState, useEffect } from 'react';
import Link from 'next/link';
import { FaFilter, FaTimes } from 'react-icons/fa';
import { Diet, Ingredient, MealType } from '../../services/TypeService';
import { Recipe } from '../../services/TypeService';
import MultiSelectAutoComplete, { Option } from '../../components/MultiSelectAutoComplete';
import { getRecipes, getAllIngredients, getAllMealTypes, getAllDiets } from '../../services/recipeService';

export default function Recipes() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [mealTypes, setMealTypes] = useState<MealType[]>([]);
  const [diets, setDiets] = useState<Diet[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<Filters>({
    ingredients: [],
    mealType: '',
    diet: '',
  });
  const [showFilters, setShowFilters] = useState(true);

  type Filters = {
    ingredients: Ingredient[];
    mealType: string;
    diet: string;
  };

  // TODO This is reloading all data every filter change I believe, could be optimized
  // Need to ensure the ingredients, mealtypes, diets are loaded first, then recipes and filter changes
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [recipesData, ingredientsData, mealTypesData, dietsData] = await Promise.all([
          getRecipes(filters),
          getAllIngredients(),
          getAllMealTypes(),
          getAllDiets(),
        ]);

        setRecipes(recipesData);
        setIngredients(ingredientsData);
        setMealTypes(mealTypesData);
        setDiets(dietsData);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [filters]);


  const handleFilterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const handleIngredientFilterChange = (e: Option[]) => {
    const mappedIngredients = e.map(ingredient => ({
      id: ingredient.id,
      name: ingredient.label,
    }))

    setFilters((prev) => ({ ...prev, ingredients: mappedIngredients }));
  }

  const clearFilters = () => {
    setFilters({
      ingredients: [],
      mealType: '',
      diet: ''
    });
  };

  const allIngredients: Option[] = ingredients.map(ingredient => ({
    id: ingredient.id,
    label: ingredient.name,
  }));

  const removeOption = (selectedOptionId: number) => {
    setFilters(prev => ({
      ...prev,
      ingredients: prev.ingredients.filter(ingredient => ingredient.id !== selectedOptionId)
    }));
  };

  return (
    <div className="space-y-6">
      {/* Filter section */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between p-4 bg-white rounded-lg shadow-md">
        <div className="flex flex-wrap gap-2">
          {/* Ingredient filter */}
          <div className="flex items-center">
            <label htmlFor="ingredients" className="mr-2 text-sm font-medium">Ingredients:</label>
            <MultiSelectAutoComplete
              options={allIngredients}
              selectedOptions={filters.ingredients.map(ingredient => ({
                id: ingredient.id,
                label: ingredient.name,
              }))}
              onChange={handleIngredientFilterChange}
            />
          </div>

          {/* Meal type filter */}
          <div className="flex items-center text-nowrap">
            <label htmlFor="mealType" className="mr-2 text-sm font-medium">Meal Type:</label>
            <select
              id="mealType"
              name="mealType"
              value={filters.mealType}
              onChange={handleFilterChange}
              className="p-2 border rounded-md text-sm form-input"
            >
              <option value="">All Meal Types</option>
              {mealTypes.map(type => (
                <option key={type.id} value={type.name}>{type.name.charAt(0).toUpperCase() + type.name.slice(1)}</option>
              ))}
            </select>
          </div>

          {/* Diet type filter */}
          <div className="flex items-center text-nowrap">
            <label htmlFor="diet" className="mr-2 text-sm font-medium">Diet Type:</label>
            <select
              id="diet"
              name="diet"
              value={filters.diet}
              onChange={handleFilterChange}
              className="p-2 border rounded-md text-sm form-input"
            >
              <option value="">All Diets</option>
              {diets.map(diet => (
                <option key={diet.id} value={diet.name}>{diet.name.charAt(0).toUpperCase() + diet.name.slice(1)}</option>
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
            {showFilters ? 'Hide Filters' : 'Show Filters'}
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
      {/* TODO Show meal type and diet before ingredient filters */}
      <div className="flex flex-wrap gap-2 mb-2"> 
        {showFilters && filters.mealType && (
          <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded flex items-center">
            {filters.mealType}
          </span>)} 
        {showFilters && filters.diet && (
          <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded flex items-center">
            {filters.diet}
          </span>
        )}
        {showFilters && filters.ingredients.map((opt) => (
          <span
            key={opt.id}
            className="bg-blue-100 text-blue-700 px-2 py-1 rounded flex items-center"
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
          recipes.map(recipe => (
            <div key={recipe.id} className="bg-white rounded-lg shadow-md overflow-hidden">
              <Link href={`/recipes/${recipe.id}`}>
                <div className="relative">
                  <img
                    src={recipe.image_url}
                    alt={recipe.title}
                    className="w-full h-48 object-cover"
                  />
                  <div className="absolute inset-0 bg-black opacity-30"></div>
                  <div className="absolute bottom-0 left-0 p-4">
                    <h3 className="text-white text-lg font-semibold">{recipe.title}</h3>
                    <p className="text-white text-sm">
                      {recipe.servings} servings • {recipe.cooking_time} min
                    </p>
                  </div>
                </div>
              </Link>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
