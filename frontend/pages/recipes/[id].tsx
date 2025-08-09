import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { getRecipeById, addShoppingListItem, Ingredient, Recipe } from '../../services/api';
import Link from 'next/link';
import { FaArrowLeft, FaClock, FaUtensils, FaList, FaCheck } from 'react-icons/fa';

export default function RecipeDetail() {
    const router = useRouter();
    const { id } = router.query as { id?: string };

    const [recipe, setRecipe] = useState<Recipe | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [addingToList, setAddingToList] = useState(false);
    const [addedItems, setAddedItems] = useState<number[]>([]);

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

    const handleAddToShoppingList = async (ingredient: Ingredient) => {
        if (addedItems.includes(ingredient.id)) return;
        setAddingToList(true);
        try {
            await addShoppingListItem({ name: ingredient.name, quantity: "1" });
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
                <Link href="/recipes" className="btn btn-primary">Back to Recipes</Link>
            </div>
        );
    }
    if (!recipe) return null;

    return (
        <div>
            <div className="max-w-4xl mx-auto px-4 py-8">
                <div className="flex items-center mb-4">
                    <Link href="/recipes" className="text-gray-500 hover:text-gray-700">
                        <FaArrowLeft className="h-5 w-5" />
                    </Link>
                    <h1 className="text-3xl font-bold ml-4">{recipe.title}</h1>
                </div>
                <div>
                    <img src={recipe.image_url} className='w-full h-56 object-cover rounded-lg sm:grid-cols-2'/>
                </div>
                <div className='bg-white rounded-lg shadow-md gap-4 p-6 mb-8'>
                    <h2 className='text-xl font-semibold mb-4'>Description</h2>
                    <p dangerouslySetInnerHTML={{__html: recipe.description}}></p>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
                    <div className="bg-white rounded-lg shadow-md p-6">
                        <h2 className="text-xl font-semibold mb-4">Details</h2>
                        <div className="flex items-center text-gray-700 mb-2">
                            <FaClock className="h-5 w-5 mr-2" />
                            <span>{recipe.cooking_time} minutes</span>
                        </div>
                        <div className="flex items-center text-gray-700 mb-2">
                            <FaUtensils className="h-5 w-5 mr-2" />
                            <span>Servings: {recipe.servings}</span>
                        </div>
                        <div className="flex items-center text-gray-700">
                            <FaList className="h-5 w-5 mr-2" />
                            <span>Meal Type: {recipe.meal_type}</span>
                        </div>
                    </div>
                    <div className="bg-white rounded-lg shadow-md p-6">
                        <h2 className="text-xl font-semibold mb-4">Diets</h2>
                        {recipe.diets && recipe.diets.length > 0 ? (
                            <ul className="list-disc list-inside">
                                {recipe.diets.map(diet => (
                                    <li key={diet.id} className="text-gray-700">{diet.name}</li>
                                ))}
                            </ul>
                        ) : (
                            <p className="text-gray-500">No specific diets for this recipe.</p>
                        )}
                    </div>
                </div>
                <div className="bg-white rounded-lg shadow-md p-6 mb-8">
                    <h2 className="text-xl font-semibold mb-4">Ingredients</h2>
                    {recipe.recipe_ingredients && recipe.recipe_ingredients.length > 0 ? (
                        <ul className="list-disc list-inside">
                            {recipe.recipe_ingredients.map(ingredient => (
                                <li key={ingredient.ingredient.id} className="flex justify-between items-center py-2">
                                    <span className="text-gray-700">{ingredient.ingredient.name}</span>
                                    <button
                                        onClick={() => handleAddToShoppingList(ingredient.ingredient)}
                                        className={`ml-4 px-3 py-1 rounded-lg text-white focus:outline-none ${addedItems.includes(ingredient.ingredient.id) ? 'bg-green-500' : 'bg-blue-500 hover:bg-blue-600'
                                            }`}
                                        disabled={addingToList}
                                    >
                                        {addedItems.includes(ingredient.ingredient.id) ? <FaCheck className="inline-block mr-1" /> : null}
                                        {addingToList && addedItems.includes(ingredient.ingredient.id) ? 'Adding...' : 'Add to Shopping List'}
                                    </button>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p className="text-gray-500">No ingredients found for this recipe.</p>
                    )}
                </div>
                <div className="bg-white rounded-lg shadow-md p-6">
                    <h2 className="text-xl font-semibold mb-4">Instructions</h2>
                    <div className="prose max-w-none">
                {Array.isArray(recipe.instructions) && recipe.instructions.length > 0 ? (
                    <ol className="list-decimal list-inside">
                        {recipe.instructions.map((step, idx) => (
                            <li key={idx} className="mb-2">{step}</li>
                        ))}
                    </ol>
                ) : (
                    <p className="text-gray-500">No instructions found for this recipe.</p>
                )}
              </div>
                </div>
            </div>
        </div>
    );
}
