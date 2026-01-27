import Link from 'next/link';
import { FiClock, FiUsers } from 'react-icons/fi';
import { Recipe } from '../services/TypeService';
import React, { useState, useEffect } from 'react';
import { FaHeart } from 'react-icons/fa';
import { addUserFavouriteRecipe, removeUserFavouriteRecipe, getUserFavouriteRecipes } from '../services/recipeService';
import { useAuth } from '../context/AuthContext';

interface RecipeCardProps {
  recipe: Recipe;
}

export default function RecipeCard({ recipe }: RecipeCardProps) {
  const { isLoggedIn } = useAuth();
  const [isFavourite, setIsFavourite] = useState(recipe.isFavourite || false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isLoggedIn) {
      const checkIfFavourite = async () => {
        try {
          const favourites = await getUserFavouriteRecipes();
          const isFav = favourites.some(fav => fav.id === recipe.id);
          setIsFavourite(isFav);
        } catch (error) {
          console.error('Failed to fetch favourite recipes:', error);
        }
      };
      checkIfFavourite();
    }
  }, [isLoggedIn, recipe.id]);

  const handleFavouriteClick = async (
    e: React.MouseEvent<HTMLButtonElement>,
    recipe: Recipe
  ) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      let result: boolean;
      
      if (isFavourite) {
        result = await removeUserFavouriteRecipe(recipe.id);
      } else {
        result = await addUserFavouriteRecipe(recipe.id);
      }
      
      if (result) {
        setIsFavourite(!isFavourite);
      }
    } catch (error) {
      console.error('Failed to update favourite status:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Link href={`/recipes/${recipe.id}`}>
      <div className="card hover:shadow-lg transition-shadow duration-300 cursor-pointer">
        <div className="h-40 bg-gray-200">
          <img
            src={recipe.image_url}
            alt={recipe.title}
            className="w-full h-full object-cover" />
        </div>
        <div className="p-4">
          <div className='flex justify-between'>
            <h3 className="text-lg font-medium text-gray-900 mb-2">{recipe.title}</h3>
            {isLoggedIn && (
              <button
                className="bg-white bg-opacity-75 rounded-full hover:bg-opacity-100 align-top disabled:opacity-50"
                onClick={(e) => handleFavouriteClick(e, recipe)}
                disabled={isLoading}
              >
              <FaHeart
                title={isFavourite ? "Remove Recipe from Favourites" : "Add Recipe to Favourites"}
                className={` ${isFavourite ? "text-red-500" : "text-gray-200"}`}
              />
            </button>
          )}
        </div>
        {(recipe.cooking_time || recipe.servings) && (
          <div className="flex items-center text-sm text-gray-500 mb-2">
            {recipe.cooking_time && (
              <>
                <FiClock className="mr-1" />
                <span>{recipe.cooking_time} minutes</span>
              </>
            )}
            {recipe.cooking_time && recipe.servings && (
              <span className="mx-2">•</span>
            )}
            {recipe.servings && (
              <>
                <FiUsers className="mr-1" />
                <span>{recipe.servings} servings</span>
              </>
            )}
          </div>
        )}
        <div className="mt-3">
          {recipe.meal_types && recipe.meal_types?.map(mealType => (
            <span
              key={mealType.id}
              className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 mr-2"
            >
              {mealType.name}
            </span>
          ))}
          {recipe.diets && recipe.diets.map(diet => (
            <span
              key={diet.id}
              className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mr-2"
            >
              {diet.name}
            </span>
          ))}
        </div>
        {/* <div className="mt-4">
          <Link
            href={`/recipes/${recipe.id}`}
            className="text-primary hover:text-primary-dark font-medium"
          >
            View Recipe
          </Link>
        </div> */}
      </div>
    </div>    </Link>  );
}