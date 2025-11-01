import { useEffect, useState } from "react";
import { FridgeItem } from "../services/TypeService";
import { addFridgeIngredient, deleteFridgeIngredient, getFridgeIngredients, updateFridgeIngredient } from "../services/fridgeService";
import { FaPlus, FaTrash } from "react-icons/fa";

// BUG Quanitity is not set on created ingredients but shows after reload
export default function Fridge() {
    const [ingredients, setIngredients] = useState<FridgeItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [newItem, setNewItem] = useState({ name: "", quantity: "" });

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const fridgeIngredients = await getFridgeIngredients();

                setIngredients(fridgeIngredients)
            } catch (error) {
                console.error("Error fetching data:", error);
            } finally {
                setLoading(false)
            }
        };

        fetchData();
    }, []);

    const handleDeleteItem = async (id: number) => {
        try {
            await deleteFridgeIngredient(id);
            setIngredients((prev) => prev.filter((item) => item.id !== id));
        } catch (err) {
            console.error("Error deleting item:", err);
            // setError("Failed to delete item");
        }
    };

    const handleUpdateQuantity = async (id: number, quantity: string) => {
        try {
            const updatedItem = await updateFridgeIngredient(id, { quantity });
            setIngredients((prev) =>
                prev.map((i) => (i.id === updatedItem.id ? updatedItem : i))
            );
        } catch (err) {
            console.error("Error updating quantity:", err);
            // setError("Failed to update quantity");
        }
    };

    const handleAddItem = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (!newItem.name.trim()) return;
        try {
            const addedItem = await addFridgeIngredient(newItem);
            setIngredients((prev) => [...prev, addedItem]);
            setNewItem({ name: "", quantity: "" });
            // setError(null);
        } catch (err) {
            console.error("Error adding item:", err);
            // setError("Failed to add item");
        }
    };

    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold">Fridge Ingredients</h1>

            {/* Add new item form */}
            <div className="card p-4">
                <h2 className="text-lg font-semibold mb-4">Add New Ingredient</h2>
                <form
                    onSubmit={handleAddItem}
                    className="flex flex-col md:flex-row gap-3"
                >
                    <input
                        type="text"
                        placeholder="Item name"
                        value={newItem.name}
                        onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
                        className="form-input flex-grow"
                        required
                    />
                    <input
                        type="text"
                        placeholder="Quantity (e.g. 2 cups)"
                        value={newItem.quantity}
                        onChange={(e) =>
                            setNewItem({ ...newItem, quantity: e.target.value })
                        }
                        className="form-input md:w-1/4"
                    />
                    <button
                        type="submit"
                        className="btn btn-primary flex items-center justify-center whitespace-nowrap"
                    >
                        <FaPlus className="mr-2" />
                        Add Item
                    </button>
                </form>
            </div>


            <div className="card p-4">
                <h2 className="text-lg font-semibold mb-4">Fridge Ingredients</h2>

                {loading ? (
                    <p className="text-center py-4">Loading Fridge...</p>
                ) : ingredients.length === 0 ? (
                    <div className="text-center py-6 text-gray-500">
                        <p>Your Fridge is empty</p>
                        <p className="text-sm mt-2">Add items using the form above</p>
                    </div>
                ) : (
                    <div>
                        <div className="mb-4">
                            {/* <h3 className="text-md font-medium">Items to buy</h3> */}
                            <ul className="divide-y">
                                {ingredients
                                    .map((item) => (
                                        <li key={item.id} className="py-3 px-1 flex items-center">
                                            <div className="flex-grow">
                                                <p className="font-medium">{item.name}</p>
                                                <div className="flex items-center">
                                                    <input
                                                        type="text"
                                                        value={item.quantity || ""}
                                                        onChange={(e) =>
                                                            handleUpdateQuantity(item.id, e.target.value)
                                                        }
                                                        placeholder="Add quantity"
                                                        className="text-sm text-gray-500 border-b border-transparent hover:border-gray-300 focus:border-primary focus:outline-none w-24"
                                                    />
                                                </div>
                                            </div>
                                            <button
                                                title="buttonDeleteItem"
                                                onClick={() => handleDeleteItem(item.id)}
                                                className="text-red-500 hover:text-red-700 ml-2"
                                            >
                                                <FaTrash />
                                            </button>
                                        </li>
                                    ))}
                            </ul>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}