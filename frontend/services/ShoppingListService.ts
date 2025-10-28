import { api } from './apiService';
import { ShoppingListItem } from './TypeService';

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
