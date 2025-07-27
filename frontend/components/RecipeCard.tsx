import Link from 'next/link';
import { FiClock, FiUsers } from 'react-icons/fi';

// Renamed to .tsx and added TypeScript types for props
interface Recipe {
  id: number;
  title: string;
  cooking_time: number;
  servings: number;
  meal_type: string;
  diets?: { id: number; name: string }[];
}

interface RecipeCardProps {
  recipe: Recipe;
}

export default function RecipeCard({ recipe }: RecipeCardProps) {
  return (
    <div className="card hover:shadow-lg transition-shadow duration-300">
      <div className="p-4">
        <h3 className="text-lg font-medium text-gray-900 mb-2">{recipe.title}</h3>
        <div className="flex items-center text-sm text-gray-500 mb-2">
          <FiClock className="mr-1" />
          <span>{recipe.cooking_time} minutes</span>
          <span className="mx-2">•</span>
          <FiUsers className="mr-1" />
          <span>{recipe.servings} servings</span>
        </div>
        <div className="mt-3">
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 mr-2">
            {recipe.meal_type}
          </span>
          {recipe.diets && recipe.diets.map(diet => (
            <span 
              key={diet.id}
              className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mr-2"
            >
              {diet.name}
            </span>
          ))}
        </div>
        <div className="mt-4">
          <Link
            href={`/recipes/${recipe.id}`}
            className="text-primary hover:text-primary-dark font-medium"
          >
            View Recipe
          </Link>
        </div>
      </div>
    </div>
  );
}
