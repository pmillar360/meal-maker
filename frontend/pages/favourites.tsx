import { useState, useEffect } from "react";
import { Recipe } from "../services/TypeService";
import { getUserFavouriteRecipes } from "../services/recipeService";
import Link from "next/link";

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
            <h1>Your Favourites</h1>
            <ul>
                {favourites.map((recipe) => (
                    <li key={recipe.id}>
                        <Link href={`/recipes/${recipe.id}`}>{recipe.title}</Link>
                    </li>
                ))}
            </ul>
        </div>
    );
}
