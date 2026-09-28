import { Recipe } from '../services/TypeService';

export const tomato = { id: 1, name: 'Tomato' };
export const pasta = { id: 2, name: 'Pasta' };

export const tomatoPasta: Recipe = {
  id: 10,
  title: 'Tomato Pasta',
  cooking_time: 25,
  servings: 2,
  meal_types: [{ id: 1, name: 'Dinner' }],
  diets: [{ id: 1, name: 'vegetarian' }],
  image_url: '/tomato-pasta.jpg',
  instructions: 'Boil the pasta.\nStir through the tomato sauce.',
  instructionSteps: [],
  recipe_ingredients: [
    { ingredient: tomato, quantity: '2', unit: 'whole' },
    { ingredient: pasta, quantity: '200', unit: 'g' },
  ],
  description: 'A quick <strong>weeknight</strong> pasta.',
  is_featured: true,
  last_updated: new Date('2026-01-01'),
};
