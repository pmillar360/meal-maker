import axios from 'axios';

// Connect to localhost:8000 if NEXT_PUBLIC_API_URL is not provided
const API_URL = process.env.NEXT_PUBLIC_API_URL 
  ? `http://${process.env.NEXT_PUBLIC_API_URL}:8000`
  : 'http://localhost:8000';


const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Recipe {
  id: number;
  title: string;
  cooking_time: number;
  servings: number;
  meal_type: string;
  diets?: { id: number; name: string }[];
  image_url: string;
  instructions: string;
  instructionSteps: string[];
  recipe_ingredients: RecipeIngredient[];
  description: string;
}

export const mealTypes = ['breakfast', 'lunch', 'dinner', 'snack']; // TODO not sure what to do with these long term, do we store this in db?  
export const dietTypes = ['vegetarian', 'vegan', 'gluten-free', 'dairy-free'];


export interface Ingredient {
  id: number;
  name: string;
  category?: string;
  spoonacular_id?: number;
}

export interface RecipeIngredient {
  ingredient: Ingredient;
  quantity: string;
  unit: string;
}

export interface ShoppingListItem {
  id: number;
  name: string;
  quantity: string;
  completed?: boolean;
}

// Recipe-related API calls
export const getRecipes = async (filters: {
  ingredients?: Ingredient[];
  mealType?: string;
  diet?: string;
} = {}): Promise<Recipe[]> => {
  const { ingredients, mealType, diet } = filters;
  let queryParams = new URLSearchParams();
  if (ingredients && ingredients.length > 0) queryParams.append('ingredients', ingredients.map(x => x.name).toString());
  if (mealType) queryParams.append('meal_type', mealType);
  if (diet) queryParams.append('diet', diet);
  const response = await api.get(`/recipes/?${queryParams}`);
  return response.data;
};

export const getFeaturedRecipes = async(): Promise<Recipe[]> => {
  const response = await api.get(`/recipes/featured/`);
  return response.data;
}

export const getRandomRecipes = async(): Promise<Recipe[]> => {
  const response = await api.get(`/recipes/random/`)
  return response.data
}

export const getRecipeById = async (id: number | string): Promise<Recipe> => {
  const response = await api.get(`/recipes/${id}`);
  return response.data;
};

export const getAllIngredients = async (): Promise<Ingredient[]> => {
  const response = await api.get('/ingredients/');
  return response.data;
};

// Shopping list API calls
export const getShoppingList = async (): Promise<ShoppingListItem[]> => {
  const response = await api.get('/shopping-list/');
  return response.data;
};

export const addShoppingListItem = async (item: Omit<ShoppingListItem, 'id'>): Promise<ShoppingListItem> => {
  const response = await api.post('/shopping-list/', item);
  return response.data;
};

export const updateShoppingListItem = async (id: number, updates: Partial<ShoppingListItem>): Promise<ShoppingListItem> => {
  const response = await api.patch(`/shopping-list/${id}`, updates);
  return response.data;
};

export const deleteShoppingListItem = async (id: number): Promise<void> => {
  await api.delete(`/shopping-list/${id}`);
};
