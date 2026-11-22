import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import Home from '../pages/index';
import { tomato, tomatoPasta } from './fixtures';

const mocks = vi.hoisted(() => ({
  isLoggedIn: false,
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
  useAuth: () => ({ isLoggedIn: mocks.isLoggedIn, isLoading: false }),
}));
vi.mock('../context/ToastContext', () => ({
  useToast: () => ({ addToast: mocks.addToast }),
}));

describe('home ingredient matching workflow', () => {
  beforeEach(() => {
    mocks.isLoggedIn = false;
    mocks.getFeaturedRecipes.mockResolvedValue([]);
    mocks.getAllIngredients.mockResolvedValue([tomato]);
    mocks.getRecipesByIngredients.mockResolvedValue([tomatoPasta]);
    mocks.getRecipeById.mockResolvedValue(tomatoPasta);
  });

  it('adds a guest fridge ingredient and shows its recipe suggestion', async () => {
    mocks.getFeaturedRecipes.mockResolvedValue([tomatoPasta, tomatoPasta]);
    mocks.getRecipesByIngredients.mockResolvedValue([tomatoPasta, tomatoPasta]);
    const user = userEvent.setup();
    render(<Home />);

    const ingredientSearch = await screen.findByPlaceholderText('Try eggs, spinach, onion...');
    await user.type(ingredientSearch, 'tom');
    await user.click(screen.getByText('Tomato'));

    expect(await screen.findByRole('button', { name: 'Tomato ×' })).toBeInTheDocument();
    await waitFor(() => expect(mocks.getRecipesByIngredients).toHaveBeenCalledWith(['Tomato'], 9));
    expect(await screen.findByText('1/2 ingredients available')).toBeInTheDocument();
    for (const name of ['What Can I Cook Right Now?', 'Featured Recipes']) {
      const section = screen.getByRole('heading', { name }).closest('section')!;
      expect(within(section).getAllByRole('heading', { name: 'Tomato Pasta' })).toHaveLength(1);
    }
    expect(mocks.getRecipeById).toHaveBeenCalledTimes(1);
  });

  it.each([false, true])('requires an on-hand ingredient for recommendations (signed in: %s)', async (signedIn) => {
    mocks.isLoggedIn = signedIn;
    const pastaOnly = { ...tomatoPasta, id: 11, title: 'Plain pasta', recipe_ingredients: tomatoPasta.recipe_ingredients.slice(1) };
    if (signedIn) {
      mocks.getFridgeIngredients.mockResolvedValue([tomato]);
      mocks.getUserFavouriteRecipes.mockResolvedValue([]);
      mocks.getRecipesWithFridgeAvailability.mockResolvedValue([
        { recipe: tomatoPasta, available_ingredients: 1, total_ingredients: 2, missing_ingredients: 1, missing_ingredient_names: ['Pasta'] },
        { recipe: pastaOnly, available_ingredients: 0, total_ingredients: 1, missing_ingredients: 1, missing_ingredient_names: ['Pasta'] },
      ]);
    } else {
      localStorage.setItem('meal-maker-local-fridge-items', JSON.stringify(['Tomato']));
      mocks.getRecipesByIngredients.mockResolvedValue([pastaOnly, tomatoPasta]);
      mocks.getRecipeById.mockImplementation(async id => id === pastaOnly.id ? pastaOnly : tomatoPasta);
    }
    render(<Home />);
    expect(await screen.findByText('1/2 ingredients available')).toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Plain pasta' })).not.toBeInTheDocument();
  });

  it('restores a guest fridge on remount and persists removals', async () => {
    const key = 'meal-maker-local-fridge-items';
    localStorage.setItem(key, JSON.stringify(['Tomato']));
    const user = userEvent.setup();
    const first = render(<Home />);

    expect(await screen.findByRole('button', { name: /^Tomato/ })).toBeInTheDocument();
    expect(await screen.findByRole('heading', { name: 'Tomato Pasta' })).toBeInTheDocument();
    first.unmount();

    render(<Home />);
    await user.click(await screen.findByRole('button', { name: /^Tomato/ }));
    expect(screen.queryByRole('button', { name: /^Tomato/ })).not.toBeInTheDocument();
    expect(JSON.parse(localStorage.getItem(key)!)).toEqual([]);
  });
});
