import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import RecipeDetail from '../pages/recipes/[id]';
import { pasta, tomato, tomatoPasta } from './fixtures';

const mocks = vi.hoisted(() => ({
  getRecipeById: vi.fn(),
  getRecipeAvailabilityById: vi.fn(),
  addMissingIngredientsToShoppingList: vi.fn(),
  addShoppingListItem: vi.fn(),
  addToast: vi.fn(),
  back: vi.fn(),
}));

vi.mock('next/router', () => ({
  useRouter: () => ({ query: { id: '10' }, back: mocks.back }),
}));
vi.mock('../services/recipeService', () => ({
  getRecipeById: mocks.getRecipeById,
  getRecipeAvailabilityById: mocks.getRecipeAvailabilityById,
  addMissingIngredientsToShoppingList: mocks.addMissingIngredientsToShoppingList,
}));
vi.mock('../services/ShoppingListService', () => ({
  addShoppingListItem: mocks.addShoppingListItem,
}));
vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({ isLoggedIn: true }),
}));
vi.mock('../context/ToastContext', () => ({
  useToast: () => ({ addToast: mocks.addToast }),
}));

describe('recipe detail workflow', () => {
  beforeEach(() => {
    mocks.getRecipeAvailabilityById.mockResolvedValue({
      recipe: tomatoPasta,
      ingredient_statuses: [
        { ingredient: tomato, has_in_fridge: true, missing: false },
        { ingredient: pasta, has_in_fridge: false, missing: true },
      ],
      total_ingredients: 2,
      available_ingredients: 1,
      missing_ingredients: 1,
      missing_ingredient_names: ['Pasta'],
    });
    mocks.addMissingIngredientsToShoppingList.mockResolvedValue({
      created_items: [{ id: 30, name: 'Pasta', quantity: '200 g' }],
      created_count: 1,
    });
  });

  it('shows complete recipe details and adds all missing ingredients', async () => {
    const user = userEvent.setup();
    render(<RecipeDetail />);

    expect(await screen.findByRole('heading', { name: 'Tomato Pasta' })).toBeInTheDocument();
    expect(screen.getByText('25 minutes')).toBeInTheDocument();
    expect(screen.getByText('Servings: 2')).toBeInTheDocument();
    expect(screen.getByText('Meal Type: Dinner')).toBeInTheDocument();
    expect(screen.getByText('vegetarian')).toBeInTheDocument();
    expect(screen.getByText('Boil the pasta.')).toBeInTheDocument();
    expect(screen.getByText('Stir through the tomato sauce.')).toBeInTheDocument();
    expect(screen.getByText('In Fridge')).toBeInTheDocument();
    expect(screen.getByText('Missing')).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: 'Add All Missing to Shopping List' }));

    await waitFor(() => expect(mocks.addMissingIngredientsToShoppingList).toHaveBeenCalledWith('10'));
    expect(mocks.addToast).toHaveBeenCalledWith(
      'Added 1 missing ingredient(s) to your shopping list.',
      'success'
    );
  });
});
