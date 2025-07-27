import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getRecipes } from '../services/api';

interface Recipe {
  id: number;
  title: string;
  cooking_time: number;
  servings: number;
  meal_type: string;
  diets?: { id: number; name: string }[];
}

export default function Home() {
  const [featuredRecipes, setFeaturedRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadFeaturedRecipes = async () => {
      try {
        const recipes = await getRecipes({ limit: 3 } as any);
        setFeaturedRecipes(recipes);
      } catch (error) {
        console.error("Failed to load featured recipes:", error);
      } finally {
        setLoading(false);
      }
    };
    loadFeaturedRecipes();
  }, []);

  return (
    <div className="space-y-10">
      {/* Hero Section */}
      <section className="rounded-xl bg-gradient-to-r from-primary-light to-primary p-8 text-white">
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
              <Link
                key={recipe.id}
                href={`/recipes/${recipe.id}`}
                className="card hover:shadow-lg transition-shadow duration-200">

                <div className="h-40 bg-gray-200"></div>
                <div className="p-4">
                  <h3 className="font-semibold text-lg mb-1">{recipe.title}</h3>
                  <p className="text-sm text-gray-500">
                    {recipe.cooking_time} mins | {recipe.meal_type}
                  </p>
                </div>

              </Link>
            ))
          ) : (
            <p className="text-gray-500">No featured recipes available</p>
          )}
        </div>
      </section>
    </div>
  );
}
