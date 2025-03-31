import { useState, useEffect } from 'react';
import { getRecipes, getAllIngredients } from '../../services/api';
import Link from 'next/link';
import { FaFilter, FaTimes } from 'react-icons/fa';

export default function Recipes() {
  const [recipes, setRecipes] = useState([]);
  const [ingredients, setIngredients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    ingredients: '',
    mealType: '',
    diet: ''
  });
  const [showFilters, setShowFilters] = useState(false);

  const mealTypes = ['breakfast', 'lunch', 'dinner', 'snack'];
  const dietTypes = ['vegetarian', 'vegan', 'gluten-free', 'dairy-free'];

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [recipesData, ingredientsData] = await Promise.all([
          getRecipes(filters),
          getAllIngredients()
        ]);
        setRecipes(recipesData);
        setIngredients(ingredientsData);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [filters]);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const clearFilters = () => {
    setFilters({
      ingredients: '',
      mealType: '',
      diet: ''
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Recipes</h1>
        <button 
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center btn btn-secondary"
        >
          <FaFilter className="mr-2" />
          {showFilters ? 'Hide Filters' : 'Show Filters'}
        </button>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="card p-4 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Filters</h2>
            <button 
              onClick={clearFilters}
              className="text-sm text-gray-500 flex items-center hover:text-primary"
            >
              <FaTimes className="mr-1" />
              Clear filters
            </button>
          </div>
          <div className="grid md:grid-cols-3 gap-4">
            <div>
              <label htmlFor="ingredients" className="form-label">Ingredients</label>
              <select
                id="ingredients"
                name="ingredients"
                value={filters.ingredients}
                onChange={handleFilterChange}
                className="form-input"
              >
                <option value="">Any ingredients</option>
                {ingredients.map(ingredient => (
                  <option key={ingredient.id} value={ingredient.name}>
                    {ingredient.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="mealType" className="form-label">Meal Type</label>
              <select
                id="mealType"
                name="mealType"
                value={filters.mealType}
                onChange={handleFilterChange}
                className="form-input"
              >
                <option value="">Any meal type</option>
                {mealTypes.map(type => (
                  <option key={type} value={type}>
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="diet" className="form-label">Dietary Restriction</label>
              <select
                id="diet"
                name="diet"
                value={filters.diet}
                onChange={handleFilterChange}
                className="form-input"
              >
                <option value="">Any diet</option>
                {dietTypes.map(diet => (
                  <option key={diet} value={diet}>
                    {diet.charAt(0).toUpperCase() + diet.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Recipe Grid */}
      {loading ? (
        <div className="text-center py-8">
          <p>Loading recipes...</p>
        </div>
      ) : recipes.length > 0 ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {recipes.map(recipe => (
            <Link key={recipe.id} href={`/recipes/${recipe.id}`}>
              <a className="card hover:shadow-lg transition-shadow duration-200">
                <div className="h-48 bg-gray-200"></div>
                <div className="p-4">
                  <div className="flex justify-between items-start">
                    <h3 className="font-semibold text-lg">{recipe.title}</h3>
                    <span className="px-2 py-1 bg-gray-100 text-xs rounded-full">
                      {recipe.meal_type}
                    </span>
                  </div>
                  <div className="flex items-center text-sm text-gray-500 mt-2">
                    <span>{recipe.cooking_time} mins</span>
                    <span className="mx-2">•</span>
                    <span>{recipe.servings} servings</span>
                  </div>
                </div>
              </a>
            </Link>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 card p-6">
          <h3 className="text-xl font-semibold mb-2">No recipes found</h3>
          <p className="text-gray-600 mb-4">Try adjusting your filters or browse all recipes</p>
          <button
            onClick={clearFilters}
            className="btn btn-primary"
          >
            Clear all filters
          </button>
        </div>
      )}
    </div>
  );
} 