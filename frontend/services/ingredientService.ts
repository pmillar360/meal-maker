import { api } from "./apiService";
import { Ingredient } from "./TypeService";

export const getAllIngredients = async (): Promise<Ingredient[]> => {
  const response = await api.get('/ingredients/');
  return response.data;
};