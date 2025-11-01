import { api } from "./apiService";
import { FridgeItem } from "./TypeService";

// TODO If no user logged in then this should still work ideally, need a different solution to allow non logged in users to use this but save to cookies or something simple
export const getFridgeIngredients = async (): Promise<FridgeItem[]> => {
  const response = await api.get('/fridge/');
  return response.data;
}

export const addFridgeIngredient = async (item: Omit<FridgeItem, 'id'>): Promise<FridgeItem> => {
  const response = await api.post('/fridge/', item);
  return response.data;
};

export const updateFridgeIngredient = async (id: number, updates: Partial<FridgeItem>): Promise<FridgeItem> => {
  const response = await api.patch(`/fridge/${id}`, updates);
  return response.data;
}

export const deleteFridgeIngredient = async (id: number): Promise<void> => {
  await api.delete(`/fridge/${id}`);
}