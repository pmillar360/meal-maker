import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import Recipes from '../pages/recipes';
import { tomato, tomatoPasta } from './fixtures';

const mocks = vi.hoisted(() => ({
  getRecipes: vi.fn(),
  getRecipesWithFridgeAvailability: vi.fn(),
  getAllMealTypes: vi.fn(),
  getAllDiets: vi.fn(),
  getAllIngredients: vi.fn(),
  getFridgeIngredients: vi.fn(),
  addToast: vi.fn(),
}));

vi.mock('next/router', () => ({
  useRouter: () => ({ isReady: true, query: {} }),
}));
vi.mock('../services/recipeService', () => ({
  getRecipes: mocks.getRecipes,
  getRecipesWithFridgeAvailability: mocks.getRecipesWithFridgeAvailability,
  getAllMealTypes: mocks.getAllMealTypes,
  getAllDiets: mocks.getAllDiets,
}));
vi.mock('../services/ingredientService', () => ({ getAllIngredients: mocks.getAllIngredients }));
vi.mock('../services/fridgeService', () => ({ getFridgeIngredients: mocks.getFridgeIngredients }));
vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({ isLoggedIn: false }),
}));
vi.mock('../context/ToastContext', () => ({
  useToast: () => ({ addToast: mocks.addToast }),
}));

describe('recipe discovery workflow', () => {
  beforeEach(() => {
    mocks.getAllIngredients.mockResolvedValue([tomato]);
    mocks.getAllMealTypes.mockResolvedValue([{ id: 1, name: 'Dinner' }]);
    mocks.getAllDiets.mockResolvedValue([{ id: 1, name: 'vegetarian' }]);
    mocks.getRecipes.mockResolvedValue([tomatoPasta]);
  });

  it('fetches recipes once on load and does not refetch when applying local fridge ingredients', async () => {
    localStorage.setItem('meal-maker-local-fridge-items', JSON.stringify(['Onion']));
    const user = userEvent.setup();
    render(<Recipes />);

    expect(await screen.findByRole('heading', { name: 'Tomato Pasta' })).toBeInTheDocument();
    await waitFor(() => expect(mocks.getRecipes).toHaveBeenCalledTimes(1));

    await user.click(screen.getByRole('checkbox', { name: 'Apply fridge ingredients' }));
    expect(screen.getByText('No recipes found.')).toBeInTheDocument();
    expect(mocks.getRecipes).toHaveBeenCalledTimes(1);

    await user.click(screen.getByRole('checkbox', { name: 'Apply fridge ingredients' }));
    expect(screen.getByRole('heading', { name: 'Tomato Pasta' })).toBeInTheDocument();
    expect(mocks.getRecipes).toHaveBeenCalledTimes(1);
  });

  it('loads recipes and applies meal type and diet filters', async () => {
    const user = userEvent.setup();
    render(<Recipes />);

    expect(await screen.findByRole('heading', { name: 'Tomato Pasta' })).toBeInTheDocument();

    const autocompleteInputs = screen.getAllByPlaceholderText('Type to search...');
    await user.type(autocompleteInputs[1], 'Dinner');
    await user.click(screen.getByText('Dinner', { selector: 'li' }));
    await user.selectOptions(screen.getByLabelText('Diet Type:'), 'vegetarian');

    await waitFor(() => {
      expect(mocks.getRecipes).toHaveBeenLastCalledWith(expect.objectContaining({
        mealTypes: [{ id: 1, name: 'Dinner' }],
        diet: 'vegetarian',
      }));
    });
    expect(screen.getAllByText('Dinner', { selector: 'span' })).toHaveLength(2);
  });
});
