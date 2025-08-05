import { useEffect, useState } from "react";
import { Ingredient, getFridgeIngredients } from "../services/api";

export default function Fridge() {
    const [ingredients, setIngredients] = useState<Ingredient[]>([]);
    const [loading, setLoading] = useState(true);

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

    return (
        <div className="space-y-6">
            
        </div>
    );
}