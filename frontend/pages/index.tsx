import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Recipe } from '../services/TypeService';
import { getFeaturedRecipes, getUserFavouriteRecipes } from '../services/recipeService';
import RecipeCard from '../components/RecipeCard';
import { useAuth } from '../context/AuthContext';

export default function Home() {
  const { isLoggedIn } = useAuth();
  const [featuredRecipes, setFeaturedRecipes] = useState<Recipe[]>([]);
  const [favouriteRecipeIds, setFavouriteRecipeIds] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadFeaturedRecipes = async () => {
      try {
        const recipes = await getFeaturedRecipes(9);
        setFeaturedRecipes(recipes);
      } catch (error) {
        console.error("Failed to load featured recipes:", error);
      } finally {
        setLoading(false);
      }
    };
    loadFeaturedRecipes();
  }, []);

  useEffect(() => {
    if (isLoggedIn) {
      const loadFavourites = async () => {
        try {
          const favourites = await getUserFavouriteRecipes();
          setFavouriteRecipeIds(favourites.map(f => f.id));
        } catch (error) {
          console.error("Failed to load favourite recipes:", error);
        }
      };
      loadFavourites();
    } else {
      setFavouriteRecipeIds([]);
    }
  }, [isLoggedIn]);

  return (
    <div className="space-y-10">
      {/* Hero Section */}
      <section className="rounded-xl bg-linear-to-r from-primary-light to-primary p-8 text-white">
        <div className="max-w-3xl mx-auto text-center space-y-6">
          <h1 className="text-4xl font-bold">Welcome to Meal Maker</h1>
          <p className="text-xl">Find recipes based on ingredients you already have</p>
          <div className="flex justify-center space-x-4">
            <Link href="/recipes" className="btn bg-white text-primary hover:bg-gray-100">
              Browse Recipes
            </Link>
            <Link
              href="/shopping-list"
              className="btn bg-primary-dark text-white hover:bg-opacity-90">
              My Shopping List
            </Link>
          </div>
        </div>
      </section>
      {/* Features Section */}
      <section className="py-8">
        <h2 className="text-2xl font-bold text-center mb-8">How It Works</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="card p-6 text-center">
            <div className="text-primary text-4xl mb-4">1</div>
            <h3 className="text-xl font-semibold mb-2">Search by Ingredients</h3>
            <p className="text-gray-600">Enter ingredients you have and find matching recipes</p>
          </div>
          <div className="card p-6 text-center">
            <div className="text-primary text-4xl mb-4">2</div>
            <h3 className="text-xl font-semibold mb-2">Save Recipes</h3>
            <p className="text-gray-600">Bookmark your favorite recipes for quick access</p>
          </div>
          <div className="card p-6 text-center">
            <div className="text-primary text-4xl mb-4">3</div>
            <h3 className="text-xl font-semibold mb-2">Create Shopping Lists</h3>
            <p className="text-gray-600">Add missing ingredients to your shopping list</p>
          </div>
        </div>
      </section>
      {/* Featured Recipes Section */}
      <section className="py-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Featured Recipes</h2>
          <Link href="/recipes" className="text-primary hover:text-primary-dark">
            View all →
          </Link>
        </div>
        <div className="grid md:grid-cols-3 gap-6">
          {loading ? (
            <p>Loading featured recipes...</p>
          ) : featuredRecipes.length > 0 ? (
            featuredRecipes.map(recipe => (
              <RecipeCard 
                key={recipe.id} 
                recipe={recipe} 
                favouriteRecipeIds={favouriteRecipeIds}
              />
            ))
          ) : (
            <p className="text-gray-500">No featured recipes available</p>
          )}
        </div>
      </section>
    </div>
  );
}
