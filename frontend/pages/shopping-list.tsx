import { useState, useEffect } from "react";
import {
    getShoppingList,
    addShoppingListItem,
    updateShoppingListItem,
    deleteShoppingListItem
} from '../services/ShoppingListService';
import { FaPlus, FaTrash, FaCheck } from "react-icons/fa";
import { ShoppingListItem } from "../services/TypeService";
import { addFridgeIngredient } from "../services/fridgeService";

export default function ShoppingList() {
    const [items, setItems] = useState<ShoppingListItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [newItem, setNewItem] = useState({ name: "", quantity: "" });
    const [error, setError] = useState<string | null>(null);
    const [addToFridge, setAddToFridge] = useState(true);

    useEffect(() => {
        fetchShoppingList();
    }, []);

    const fetchShoppingList = async () => {
        setLoading(true);
        try {
            const data = await getShoppingList();
            setItems(data);
            setError(null);
        } catch (err) {
            console.error("Error fetching shopping list:", err);
            setError("Failed to load shopping list");
        } finally {
            setLoading(false);
        }
    };

    const handleAddItem = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (!newItem.name.trim()) return;
        try {
            const addedItem = await addShoppingListItem(newItem);
            setItems((prev) => [...prev, addedItem]);
            setNewItem({ name: "", quantity: "" });
            setError(null);
        } catch (err) {
            console.error("Error adding item:", err);
            setError("Failed to add item");
        }
    };

    const handleToggleComplete = async (item: ShoppingListItem) => {
        try {
            const updatedItem = await updateShoppingListItem(item.id, {
                completed: !item.completed,
            });
            setItems((prev) =>
                prev.map((i) => (i.id === updatedItem.id ? updatedItem : i))
            );

            if (item.completed === false && addToFridge) {
                // If marking as completed and addToFridge is true, add to fridge
                await addFridgeIngredient({ name: item.name, quantity: item.quantity || "" });// Ignoring result
            }
        } catch (err) {
            console.error("Error updating item:", err);
            setError("Failed to update item");
        }
    };

    const handleDeleteItem = async (id: number) => {
        try {
            await deleteShoppingListItem(id);
            setItems((prev) => prev.filter((item) => item.id !== id));
        } catch (err) {
            console.error("Error deleting item:", err);
            setError("Failed to delete item");
        }
    };

    const handleUpdateQuantity = async (id: number, quantity: string) => {
        try {
            const updatedItem = await updateShoppingListItem(id, { quantity });
            setItems((prev) =>
                prev.map((i) => (i.id === updatedItem.id ? updatedItem : i))
            );
        } catch (err) {
            console.error("Error updating quantity:", err);
            setError("Failed to update quantity");
        }
    };

    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold">Shopping List</h1>

            {error && (
                <div className="bg-red-100 text-red-700 p-3 rounded-md">{error}</div>
            )}

            {/* Add new item form */}
            <div className="card p-4">
                <h2 className="text-lg font-semibold mb-4">Add New Item</h2>
                <form
                    onSubmit={handleAddItem}
                    className="flex flex-col md:flex-row gap-3"
                >
                    <input
                        type="text"
                        placeholder="Item name"
                        value={newItem.name}
                        onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
                        className="form-input grow"
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

            {/* Shopping list */}
            <div className="card p-4">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-lg font-semibold">Shopping List Items</h2>

                    <div>
                        <input type="checkbox" name="addCompletedCheckbox" checked={addToFridge} onChange={(e) => setAddToFridge(e.target.checked)} />
                        <label className="ml-2">Add completed items to Fridge</label>
                    </div>
                </div>

                {loading ? (
                    <p className="text-center py-4">Loading shopping list...</p>
                ) : items.length === 0 ? (
                    <div className="text-center py-6 text-gray-500">
                        <p>Your shopping list is empty</p>
                        <p className="text-sm mt-2">Add items using the form above</p>
                    </div>
                ) : (
                    <div>
                        <div className="mb-4">
                            <ul className="divide-y">
                                {items
                                    .filter((item) => !item.completed)
                                    .map((item) => (
                                        <li key={item.id} className="py-3 px-1 flex items-center">
                                            <button
                                                title="buttonToggleComplete"
                                                onClick={() => handleToggleComplete(item)}
                                                className="w-6 h-6 rounded-full border-2 border-primary shrink-0 mr-3"
                                            />
                                            <div className="grow">
                                                <p className="font-medium">{item.name}</p>
                                                <div className="flex items-center">
                                                    <input
                                                        type="text"
                                                        value={item.quantity || ""}
                                                        onChange={(e) =>
                                                            handleUpdateQuantity(item.id, e.target.value)
                                                        }
                                                        placeholder="Add quantity"
                                                        className="text-sm text-gray-500 border-b border-transparent hover:border-gray-300 focus:border-primary focus:outline-hidden w-24"
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

                        {/* Completed items */}
                        {items.some((item) => item.completed) && (
                            <div>
                                <h3 className="text-md font-medium mb-2">Completed items</h3>
                                <ul className="divide-y">
                                    {items
                                        .filter((item) => item.completed)
                                        .map((item) => (
                                            <li
                                                key={item.id}
                                                className="py-3 px-1 flex items-center text-gray-500"
                                            >
                                                <button
                                                    title="buttonToggleComplete"
                                                    onClick={() => handleToggleComplete(item)}
                                                    className="w-6 h-6 rounded-full bg-primary text-white flex items-center justify-center shrink-0 mr-3"
                                                >
                                                    <FaCheck size={12} />
                                                </button>
                                                <div className="grow">
                                                    <p className="line-through">{item.name}</p>
                                                    {item.quantity && (
                                                        <p className="text-sm line-through">
                                                            {item.quantity}
                                                        </p>
                                                    )}
                                                </div>
                                                <button
                                                    title="buttonDeleteItem"
                                                    onClick={() => handleDeleteItem(item.id)}
                                                    className="text-red-400 hover:text-red-600 ml-2"
                                                >
                                                    <FaTrash />
                                                </button>
                                            </li>
                                        ))}
                                </ul>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
