import { useEffect, useState } from 'react'
import { Ingredient, getAllIngredients } from '../../services/api'

export default function Ingredients() {
    const [loading, setLoading] = useState(true);
    const [ingredients, setIngredients] = useState<Ingredient[]>([]);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const ingredientsData = await getAllIngredients();

                console.log(ingredientsData);
                setIngredients(ingredientsData)
            } catch (error) {
                console.error("Error fetching data:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    return (
        <div className="space-y-6">
            <div className='grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-5'>
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
                            <div className='flex justify-between items-center p-4'>
                                <div className='text-lg font-semibold'>
                                    <h3>{ingredient.name}</h3>
                                </div>
                                <p className='font-semibold text-lg'>+F</p> {/* TODO Implement the "Add to fridge" and "Add to shopping list" functions */}
                                <p className='font-semibold text-lg'>+S</p>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    )
}