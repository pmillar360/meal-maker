import { expect, it, vi } from 'vitest';
import { api } from '../services/apiService';
import { getRecipes, getRecipesWithFridgeAvailability } from '../services/recipeService';

vi.mock('../services/apiService', () => ({
  api: { get: vi.fn().mockResolvedValue({ data: [] }) },
}));

it('sends each selected ingredient ID to both recipe list endpoints', async () => {
  const filters = {
    ingredients: [{ id: 7, name: 'Onion, chopped' }, { id: 12, name: 'Garlic' }],
  };

  await getRecipes(filters);
  await getRecipesWithFridgeAvailability(filters);

  expect(api.get).toHaveBeenNthCalledWith(1, '/recipes/?ingredient_ids=7&ingredient_ids=12');
  expect(api.get).toHaveBeenNthCalledWith(2, '/recipes/with-fridge-availability/?ingredient_ids=7&ingredient_ids=12');
});
