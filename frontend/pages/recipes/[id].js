import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { getRecipeById, addShoppingListItem } from '../../services/api';
import Link from 'next/link';
import { FaArrowLeft, FaClock, FaUtensils, FaList, FaCheck } from 'react-icons/fa';

export default function RecipeDetail() {
  const router = useRouter();
  const { id } = router.query;
  
  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [addingToList, setAddingToList] = useState(false);
  const [addedItems, setAddedItems] = useState([]);

  useEffect(() => {
    if (!id) return;

    const fetchRecipe = async () => {
      setLoading(true);
      try {
        const data = await getRecipeById(id);
        setRecipe(data);
        setError(null);
      } catch (err) {
        console.error("Error fetching recipe:", err);
        setError("Failed to load recipe details");
      } finally {
        setLoading(false);
      }
    };

    fetchRecipe();
  }, [id]);

  const handleAddToShoppingList = async (ingredient) => {
    if (addedItems.includes(ingredient.id)) return;
    
    setAddingToList(true);
    try {
      await addShoppingListItem({ 
        name: ingredient.name,
        quantity: "1" // Default quantity
      });
      setAddedItems(prev => [...prev, ingredient.id]);
    } catch (error) {
      console.error("Error adding to shopping list:", error);
    } finally {
      setAddingToList(false);
    }
  };

  if (loading) {
    return <div className="text-center py-10">Loading recipe details...</div>;
  }

  if (error) {
    return (
      <div className="text-center py-10">
        <p className="text-red-500 mb-4">{error}</p>
        <Link href="/recipes" className="btn btn-primary">
          Back to Recipes
        </Link>
      </div>
    );
  }

  if (!recipe) {
    return null;
  }

  return (
    <div>
      <div className="mb-6">
        <Link
          href="/recipes"
          className="inline-flex items-center text-primary hover:text-primary-dark">

          <FaArrowLeft className="mr-2" />Back to recipes
                    
        </Link>
      </div>
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        {/* Recipe Header */}
        <div className="h-64 bg-gray-200 flex items-end">
          <div className="w-full bg-gradient-to-t from-black to-transparent p-6">
            <h1 className="text-3xl font-bold text-white">{recipe.title}</h1>
          </div>
        </div>

        {/* Recipe Info */}
        <div className="p-6">
          <div className="flex flex-wrap gap-4 mb-6 text-sm">
            <div className="flex items-center text-gray-600">
              <FaClock className="mr-2 text-primary" />
              <span>{recipe.cooking_time} minutes</span>
            </div>
            <div className="flex items-center text-gray-600">
              <FaUtensils className="mr-2 text-primary" />
              <span>{recipe.servings} servings</span>
            </div>
            <div className="flex items-center text-gray-600">
              <span className="px-2 py-1 bg-primary bg-opacity-10 text-primary rounded-full text-xs">
                {recipe.meal_type}
              </span>
            </div>
            {recipe.diets && recipe.diets.map(diet => (
              <div key={diet.id} className="flex items-center text-gray-600">
                <span className="px-2 py-1 bg-gray-100 rounded-full text-xs">
                  {diet.name}
                </span>
              </div>
            ))}
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Ingredients Column */}
            <div className="md:col-span-1">
              <div className="mb-4">
                <h2 className="text-xl font-semibold mb-4">Ingredients</h2>
                <div className="flex justify-between items-center mb-3">
                  <span className="text-sm text-gray-600">{recipe.ingredients?.length || 0} items</span>
                  <button
                    onClick={() => recipe.ingredients?.forEach(ingredient => {
                      if (!addedItems.includes(ingredient.id)) {
                        handleAddToShoppingList(ingredient);
                      }
                    })}
                    disabled={addingToList || (recipe.ingredients && recipe.ingredients.every(ingredient => addedItems.includes(ingredient.id)))}
                    className="text-sm px-3 py-1 rounded bg-primary text-white hover:bg-primary-dark disabled:bg-gray-300 disabled:text-gray-500 flex items-center"
                  >
                    <FaList className="mr-1" />
                    Add all to list
                  </button>
                </div>
                <ul className="space-y-3">
                  {recipe.ingredients && recipe.ingredients.map(ingredient => (
                    <li 
                      key={ingredient.id} 
                      className="flex justify-between items-center p-2 border-b"
                    >
                      <span>{ingredient.name}</span>
                      <button
                        onClick={() => handleAddToShoppingList(ingredient)}
                        disabled={addingToList || addedItems.includes(ingredient.id)}
                        className={`text-sm px-2 py-1 rounded ${
                          addedItems.includes(ingredient.id)
                            ? 'bg-green-100 text-green-600 flex items-center'
                            : 'bg-gray-100 hover:bg-primary hover:text-white'
                        }`}
                      >
                        {addedItems.includes(ingredient.id) ? (
                          <>
                            <FaCheck className="mr-1" />
                            Added
                          </>
                        ) : (
                          <FaList className="mr-1" />
                        )}
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Instructions Column */}
            <div className="md:col-span-2">
              <h2 className="text-xl font-semibold mb-4">Instructions</h2>
              <div className="prose max-w-none">
                {recipe.instructions.split('\n').map((paragraph, index) => {
                  // Insert a new line before numbered steps (e.g., "2.")
                  const formattedParagraph = paragraph.replace(/(\d+\.)/g, '\n$1').trim();
                  
                  return (
                    <p key={index} className="mb-4 whitespace-pre-line">{formattedParagraph}</p>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 