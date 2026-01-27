import { useState, useEffect } from "react";
import { Recipe } from "../services/TypeService";
import { getUserFavouriteRecipes } from "../services/recipeService";
import RecipeCard from "../components/RecipeCard";

export default function Favourites() {
    const [favourites, setFavourites] = useState<Recipe[]>([]);

    useEffect(() => {
        const fetchFavourites = async () => {
            const favs = await getUserFavouriteRecipes();
            if (favs) {
                setFavourites(favs);
            }
        };
        fetchFavourites();
    }, []);

    return (
        <div>
            <h1 className="text-3xl font-bold mb-4">Your Favourites</h1>
            <ul>
                {favourites.map((recipe) => (
                    <li key={recipe.id}>
                        <RecipeCard recipe={recipe} />
                    </li>
                ))}
            </ul>
        </div>
    );
}
