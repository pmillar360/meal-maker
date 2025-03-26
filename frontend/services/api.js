import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Recipe-related API calls
export const getRecipes = async (filters = {}) => {
  const { ingredients, mealType, diet } = filters;
  
  let queryParams = new URLSearchParams();
  if (ingredients) queryParams.append('ingredients', ingredients);
  if (mealType) queryParams.append('meal_type', mealType);
  if (diet) queryParams.append('diet', diet);
  
  const response = await api.get(`/recipes/?${queryParams}`);
  return response.data;
};

export const getRecipeById = async (id) => {
  const response = await api.get(`/recipes/${id}`);
  return response.data;
};

export const getAllIngredients = async () => {
  const response = await api.get('/ingredients/');
  return response.data;
};

// Shopping list API calls
export const getShoppingList = async () => {
  const response = await api.get('/shopping-list/');
  return response.data;
};

export const addShoppingListItem = async (item) => {
  const response = await api.post('/shopping-list/', item);
  return response.data;
};

export const updateShoppingListItem = async (id, updates) => {
  const response = await api.patch(`/shopping-list/${id}`, updates);
  return response.data;
};

export const deleteShoppingListItem = async (id) => {
  const response = await api.delete(`/shopping-list/${id}`);
  return response.data;
};
