import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import RecipeImage from '../../components/RecipeImage';
import { addShoppingListItem } from '../../services/ShoppingListService';
import { RecipeIngredient, RecipeIngredientAvailability } from '../../services/TypeService';
import { Recipe } from '../../services/TypeService';
import Link from 'next/link';
import { FaArrowLeft, FaClock, FaUtensils, FaList, FaCheck } from 'react-icons/fa';
import { addMissingIngredientsToShoppingList, getRecipeAvailabilityById, getRecipeById } from '../../services/recipeService';
import { useToast } from '../../context/ToastContext';
import { toastCopy } from '../../services/toastCopy';
import { useAuth } from '../../context/AuthContext';

function descriptionText(html: string): string {
    // Template contents are inert. Only their text is passed to React.
    const template = document.createElement('template');
    template.innerHTML = html;
    template.content.querySelectorAll('script, style').forEach((element) => element.remove());
    template.content.querySelectorAll('br, div, li, p').forEach((element) => element.after(' '));
    return template.content.textContent?.trim() ?? '';
}

export default function RecipeDetail() {
    const router = useRouter();
    const { id } = router.query as { id?: string };
    const { addToast } = useToast();
    const { isLoggedIn } = useAuth();

    const [recipe, setRecipe] = useState<Recipe | null>(null);
    const [ingredientStatuses, setIngredientStatuses] = useState<Record<number, RecipeIngredientAvailability>>({});
    const [missingIngredientCount, setMissingIngredientCount] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [addingToList, setAddingToList] = useState(false);
    const [addedItems, setAddedItems] = useState<number[]>([]);
    const [addingMissingIngredients, setAddingMissingIngredients] = useState(false);
    const mealTypeNames = recipe?.meal_types?.map((mealType) => mealType.name).filter(Boolean) ?? [];

    useEffect(() => {
        if (!id) return;
        let active = true;
        setAddedItems([]);
        const fetchRecipe = async () => {
            setLoading(true);
            try {
                if (isLoggedIn) {
                    const availability = await getRecipeAvailabilityById(id);
                    if (!active) return;
                    setRecipe(availability.recipe);
                    setMissingIngredientCount(availability.missing_ingredients);
                    const nextStatuses: Record<number, RecipeIngredientAvailability> = {};
                    availability.ingredient_statuses.forEach((status) => {
                        nextStatuses[status.ingredient.id] = status;
                    });
                    setIngredientStatuses(nextStatuses);
                } else {
                    const data = await getRecipeById(id);
                    if (!active) return;
                    setRecipe(data);
                    setMissingIngredientCount(0);
                    setIngredientStatuses({});
                }
                setError(null);
            } catch (err) {
                if (!active) return;
                console.error("Error fetching recipe:", err);
                setError("Failed to load recipe details");
            } finally {
                if (active) setLoading(false);
            }
        };
        fetchRecipe();
        return () => { active = false; };
    }, [id, isLoggedIn]);

    const handleAddToShoppingList = async (ingredient: RecipeIngredient) => {
        if (addedItems.includes(ingredient.id ?? ingredient.ingredient.id)) return;
        setAddingToList(true);
        try {
            await addShoppingListItem({ name: ingredient.ingredient.name, quantity: ingredient.amount ?? [ingredient.quantity, ingredient.unit].filter(Boolean).join(" ") });
            setAddedItems(prev => [...prev, ingredient.id ?? ingredient.ingredient.id]);
            addToast(toastCopy.shoppingList.added(ingredient.ingredient.name), 'success');
        } catch (error) {
            console.error("Error adding to shopping list:", error);
            addToast(toastCopy.shoppingList.addFailed(ingredient.ingredient.name), 'error');
        } finally {
            setAddingToList(false);
        }
    };

    const handleAddMissingIngredients = async () => {
        if (!id || !isLoggedIn) {
            return;
        }

        setAddingMissingIngredients(true);
        try {
            const result = await addMissingIngredientsToShoppingList(id);
            if (result.created_count === 0) {
                addToast('No missing ingredients to add.', 'success');
            } else {
                addToast(`Added ${result.created_count} missing ingredient(s) to your shopping list.`, 'success');
                setAddedItems((prev) => [
                    ...new Set([
                        ...prev,
                        ...(recipe?.recipe_ingredients ?? [])
                            .filter(line => result.created_items.some(item => item.name === line.ingredient.name))
                            .map(line => line.id ?? line.ingredient.id),
                    ]),
                ]);
                setMissingIngredientCount((prev) => Math.max(0, prev - result.created_count));
            }
        } catch (err) {
            console.error('Error adding missing ingredients:', err);
            addToast('Failed to add missing ingredients to shopping list.', 'error');
        } finally {
            setAddingMissingIngredients(false);
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
                    <button
                        type="button"
                        onClick={() => router.back()}
                        className="text-gray-500 hover:text-gray-700"
                        aria-label="Go back"
                    >
                        <FaArrowLeft className="h-5 w-5" />
                    </button>
                    <h1 className="text-3xl font-bold ml-4">{recipe.title}</h1>
                </div>
                <div className="relative h-56 w-full overflow-hidden rounded-lg">
                    <RecipeImage src={recipe.image_url} title={recipe.title} />
                </div>
                {(recipe.description || recipe.source_url) && <div className='bg-white rounded-lg shadow-md gap-4 p-6 mb-8'>
                    {recipe.description && <h2 className='text-xl font-semibold mb-4'>Description</h2>}
                    {recipe.source_url && <a className="underline" href={recipe.source_url}>Original recipe</a>}
                    <p>{recipe.provider ? recipe.description : descriptionText(recipe.description ?? '')}</p>
                </div>}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
                    <div className="bg-white rounded-lg shadow-md p-6">
                        <h2 className="text-xl font-semibold mb-4">Details</h2>
                        {recipe.cooking_time != null && <div className="flex items-center text-gray-700 mb-2">
                            <FaClock className="h-5 w-5 mr-2" />
                            <span>{recipe.cooking_time} minutes</span>
                        </div>}
                        {recipe.servings != null && <div className="flex items-center text-gray-700 mb-2">
                            <FaUtensils className="h-5 w-5 mr-2" />
                            <span>Servings: {recipe.servings}</span>
                        </div>}
                        <div className="flex items-center text-gray-700">
                            <FaList className="h-5 w-5 mr-2" />
                            <span>Meal Type: {mealTypeNames.length > 0 ? mealTypeNames.join(', ') : 'Not specified'}</span>
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
                    <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                        <h2 className="text-xl font-semibold">Ingredients</h2>
                        {isLoggedIn ? (
                            <button
                                onClick={handleAddMissingIngredients}
                                disabled={addingMissingIngredients || missingIngredientCount === 0}
                                className="btn btn-primary disabled:opacity-50"
                            >
                                {addingMissingIngredients ? 'Adding Missing Ingredients...' : 'Add All Missing to Shopping List'}
                            </button>
                        ) : (
                            <p className="text-sm text-gray-500">Log in to see availability and add all missing ingredients.</p>
                        )}
                    </div>
                    {recipe.recipe_ingredients && recipe.recipe_ingredients.length > 0 ? (
                        <div className="overflow-x-auto">
                            <table className="w-full min-w-[40rem] border-collapse">
                                <thead>
                                    <tr className="text-left text-sm text-gray-500 border-b">
                                        <th className="py-2 pr-4 font-medium">Ingredient</th>
                                        <th className="py-2 px-4 font-medium text-center w-40">Amount</th>
                                        <th className="py-2 px-4 font-medium text-center w-40">Status</th>
                                        <th className="py-2 pl-4 font-medium text-center w-60">Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {recipe.recipe_ingredients.map(ingredient => (
                                        <tr key={ingredient.id ?? ingredient.ingredient.id} className="border-b last:border-b-0">
                                            <td className="py-3 pr-4 text-gray-700 wrap-break-word">{ingredient.ingredient.name}{ingredient.preparation && <small className="block">{ingredient.preparation}</small>}</td>
                                            <td className="py-3 px-4 text-center whitespace-nowrap text-gray-700">{ingredient.amount ?? [ingredient.quantity, ingredient.unit].filter(Boolean).join(' ')}</td>
                                            <td className="py-3 px-4 text-center whitespace-nowrap">
                                                {isLoggedIn && ingredientStatuses[ingredient.ingredient.id] ? (
                                                    ingredientStatuses[ingredient.ingredient.id].has_in_fridge ? (
                                                        <span className="rounded-full bg-green-100 px-2 py-1 text-xs font-semibold text-green-800">In Fridge</span>
                                                    ) : (
                                                        <span className="rounded-full bg-amber-100 px-2 py-1 text-xs font-semibold text-amber-800">Missing</span>
                                                    )
                                                ) : (
                                                    <span className="text-xs text-gray-400">-</span>
                                                )}
                                            </td>
                                            <td className="py-3 pl-4 text-center">
                                                <button
                                                    onClick={() => handleAddToShoppingList(ingredient)}
                                                    className={`min-w-44 px-3 py-1 rounded-lg text-white focus:outline-hidden ${addedItems.includes(ingredient.id ?? ingredient.ingredient.id) ? 'bg-green-500' : 'bg-blue-500 hover:bg-blue-600'
                                                        }`}
                                                    disabled={addingToList}
                                                >
                                                    {addedItems.includes(ingredient.id ?? ingredient.ingredient.id) ? <FaCheck className="inline-block mr-1" /> : null}
                                                    {addingToList && addedItems.includes(ingredient.id ?? ingredient.ingredient.id) ? 'Adding...' : 'Add to Shopping List'}
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <p className="text-gray-500">No ingredients found for this recipe.</p>
                    )}
                </div>
                <div className="bg-white rounded-lg shadow-md p-6">
                    <h2 className="text-xl font-semibold mb-4">Instructions</h2>
                    <div className="prose max-w-none">
                {recipe.instruction_sections?.length || recipe.instructions ? (
                    (recipe.instruction_sections ?? [{ name: '', steps: recipe.instructions?.split('\n') ?? [] }]).map((section, index) => (
                        <div key={index}>
                            {section.name && <h3 className="font-semibold">{section.name}</h3>}
                            <ol className="list-decimal list-inside">
                                {section.steps.map((step, i) => <li key={i} className="mb-2">{step}</li>)}
                            </ol>
                        </div>
                    ))
                ) : (
                    <p className="text-gray-500">No instructions found for this recipe.</p>
                )}
              </div>
                </div>
            </div>
        </div>
    );
}
