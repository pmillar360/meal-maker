import { useEffect, useState } from 'react'
import { Ingredient } from '../../services/TypeService';
import { getAllIngredients } from '../../services/ingredientService';
import { addFridgeIngredient } from '../../services/fridgeService';
import { addShoppingListItem } from '../../services/ShoppingListService';
import { TbFridge } from "react-icons/tb";
import { FiShoppingCart } from "react-icons/fi";
import { useToast } from '../../context/ToastContext';
import { toastCopy } from '../../services/toastCopy';

export default function Ingredients() {
    const [loading, setLoading] = useState(true);
    const [ingredients, setIngredients] = useState<Ingredient[]>([]);
    const { addToast } = useToast();

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const ingredientsData = await getAllIngredients();

                setIngredients(ingredientsData)
            } catch (error) {
                console.error("Error fetching data:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const handleAddToFridge = async (ingredient: Ingredient) => {
        const fridgeItem = {
            name: ingredient.name,
            quantity: "", // Default quantity, can be updated later
        };

        try {
            await addFridgeIngredient(fridgeItem);
            addToast(toastCopy.fridge.added(ingredient.name), 'success');
        } catch (error) {
            console.error('Error adding ingredient to fridge:', error);
            addToast(toastCopy.fridge.addFailed(ingredient.name), 'error');
        }
    }

    const handleAddToShoppingList = async (ingredient: Ingredient) => {
        const shoppingListItem = {
            name: ingredient.name,
            quantity: "", // Default quantity, can be updated later
        };

        try {
            await addShoppingListItem(shoppingListItem);
            addToast(toastCopy.shoppingList.added(ingredient.name), 'success');
        } catch (error) {
            console.error('Error adding ingredient to shopping list:', error);
            addToast(toastCopy.shoppingList.addFailed(ingredient.name), 'error');
        }
    }

    return (
        <div className="space-y-6">
            <h1 className='text-3xl font-bold'>All Ingredients</h1>
            {loading ? (
                <p>Loading...</p>
            ) : (
                <div className='grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3'>
                    {loading ? (
                        <div className='col-span-full text-center py-10'>
                            <p className='text-lg text-gray-500'>Loading ingredients...</p>
                        </div>
                    ) : ingredients.length === 0 ? (
                        <div className='col-span-full text-center py-10'>
                            <p className='text-lg text-gray-500'>No ingredients found.</p>
                        </div>
                    ) : (
                        ingredients.map(ingredient => (
                            <div key={ingredient.id} className='bg-white rounded-lg shadow-md overflow-hidden'>
                                <div className='flex justify-between p-4'>
                                    <div className='text-lg font-semibold'>
                                        <h3>{ingredient.name}</h3>
                                    </div>
                                    <div>
                                        <button title='Add ingredient to Fridge' className='font-semibold text-lg border-2 border-transparent hover:border-green-500' onClick={() => handleAddToFridge(ingredient)}><TbFridge /></button> {/* TODO These buttons should turn green or something to indicate success */}
                                        <button title='Add ingredient to Shopping List' className='font-semibold text-lg border-2 border-transparent hover:border-green-500' onClick={() => handleAddToShoppingList(ingredient)}><FiShoppingCart /></button>
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            )}
        </div>
    )
}