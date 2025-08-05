import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
}

export interface Ingredient {
  id: number;
  name: string;
}

export interface ShoppingListItem {
  id: number;
  name: string;
  quantity: string;
  completed?: boolean;
}

// Recipe-related API calls
export const getRecipes = async (filters: {
  ingredients?: string;
  mealType?: string;
  diet?: string;
} = {}): Promise<Recipe[]> => {
  const { ingredients, mealType, diet } = filters;
  let queryParams = new URLSearchParams();
  if (ingredients) queryParams.append('ingredients', ingredients);
  if (mealType) queryParams.append('meal_type', mealType);
  if (diet) queryParams.append('diet', diet);
  const response = await api.get(`/recipes/?${queryParams}`);
  return response.data;
};

export const getExternalRecipes = async(params = {}) => {
  const queryParams = new URLSearchParams(params).toString();
  const response = await api.get(`/external-recipes/?${queryParams}`);
  return response.data;
};

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
