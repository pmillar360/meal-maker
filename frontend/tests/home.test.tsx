import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import Home from '../pages/index';
import { tomato, tomatoPasta } from './fixtures';

const mocks = vi.hoisted(() => ({
  getFeaturedRecipes: vi.fn(),
  getRecipeById: vi.fn(),
  getRecipesByIngredients: vi.fn(),
  getRecipesWithFridgeAvailability: vi.fn(),
  getUserFavouriteRecipes: vi.fn(),
  getAllIngredients: vi.fn(),
  addFridgeIngredient: vi.fn(),
  deleteFridgeIngredient: vi.fn(),
  getFridgeIngredients: vi.fn(),
  addToast: vi.fn(),
}));

vi.mock('../services/recipeService', () => ({
  getFeaturedRecipes: mocks.getFeaturedRecipes,
  getRecipeById: mocks.getRecipeById,
  getRecipesByIngredients: mocks.getRecipesByIngredients,
  getRecipesWithFridgeAvailability: mocks.getRecipesWithFridgeAvailability,
  getUserFavouriteRecipes: mocks.getUserFavouriteRecipes,
}));
vi.mock('../services/ingredientService', () => ({ getAllIngredients: mocks.getAllIngredients }));
vi.mock('../services/fridgeService', () => ({
  addFridgeIngredient: mocks.addFridgeIngredient,
  deleteFridgeIngredient: mocks.deleteFridgeIngredient,
  getFridgeIngredients: mocks.getFridgeIngredients,
}));
vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({ isLoggedIn: false }),
}));
vi.mock('../context/ToastContext', () => ({
  useToast: () => ({ addToast: mocks.addToast }),
}));

describe('home ingredient matching workflow', () => {
  beforeEach(() => {
    mocks.getFeaturedRecipes.mockResolvedValue([]);
    mocks.getAllIngredients.mockResolvedValue([tomato]);
    mocks.getRecipesByIngredients.mockResolvedValue([tomatoPasta]);
    mocks.getRecipeById.mockResolvedValue(tomatoPasta);
  });

  it('adds a guest fridge ingredient and shows its recipe suggestion', async () => {
    const user = userEvent.setup();
    render(<Home />);

    const ingredientSearch = await screen.findByPlaceholderText('Try eggs, spinach, onion...');
    await user.type(ingredientSearch, 'tom');
    await user.click(screen.getByText('Tomato'));

    expect(await screen.findByRole('button', { name: 'Tomato ×' })).toBeInTheDocument();
    await waitFor(() => expect(mocks.getRecipesByIngredients).toHaveBeenCalledWith(['Tomato'], 9));
    expect(await screen.findByRole('heading', { name: 'Tomato Pasta' })).toBeInTheDocument();
    expect(screen.getByText('1/2 ingredients available')).toBeInTheDocument();
  });
});
