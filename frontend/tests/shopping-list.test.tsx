import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import ShoppingList from '../pages/shopping-list';

const mocks = vi.hoisted(() => ({
  getShoppingList: vi.fn(),
  addShoppingListItem: vi.fn(),
  updateShoppingListItem: vi.fn(),
  deleteShoppingListItem: vi.fn(),
  addFridgeIngredient: vi.fn(),
  addToast: vi.fn(),
}));

vi.mock('../services/ShoppingListService', () => ({
  getShoppingList: mocks.getShoppingList,
  addShoppingListItem: mocks.addShoppingListItem,
  updateShoppingListItem: mocks.updateShoppingListItem,
  deleteShoppingListItem: mocks.deleteShoppingListItem,
}));
vi.mock('../services/fridgeService', () => ({
  addFridgeIngredient: mocks.addFridgeIngredient,
}));
vi.mock('../context/ToastContext', () => ({
  useToast: () => ({ addToast: mocks.addToast }),
}));

describe('shopping list workflow', () => {
  beforeEach(() => {
    mocks.getShoppingList.mockResolvedValue([
      { id: 1, name: 'Tomato', quantity: '2', completed: false },
    ]);
    mocks.addShoppingListItem.mockResolvedValue({
      id: 2,
      name: 'Pasta',
      quantity: '200 g',
      completed: false,
    });
    mocks.updateShoppingListItem.mockResolvedValue({
      id: 1,
      name: 'Tomato',
      quantity: '2',
      completed: true,
    });
    mocks.addFridgeIngredient.mockResolvedValue({ id: 5, name: 'Tomato', quantity: '2' });
    mocks.deleteShoppingListItem.mockResolvedValue(undefined);
  });

  it('adds, completes, moves to the fridge, and deletes items', async () => {
    const user = userEvent.setup();
    render(<ShoppingList />);

    const tomatoRow = (await screen.findByText('Tomato')).closest('li');
    expect(tomatoRow).not.toBeNull();

    await user.type(screen.getByPlaceholderText('Item name'), 'Pasta');
    await user.type(screen.getByPlaceholderText('Quantity (e.g. 2 cups)'), '200 g');
    await user.click(screen.getByRole('button', { name: 'Add Item' }));

    expect(mocks.addShoppingListItem).toHaveBeenCalledWith({ name: 'Pasta', quantity: '200 g' });
    expect(await screen.findByText('Pasta')).toBeInTheDocument();

    await user.click(within(tomatoRow!).getByTitle('buttonToggleComplete'));
    await waitFor(() => {
      expect(mocks.updateShoppingListItem).toHaveBeenCalledWith(1, { completed: true });
      expect(mocks.addFridgeIngredient).toHaveBeenCalledWith({ name: 'Tomato', quantity: '2' });
    });
    expect(screen.getByRole('heading', { name: 'Completed items' })).toBeInTheDocument();

    const pastaRow = screen.getByText('Pasta').closest('li');
    await user.click(within(pastaRow!).getByTitle('buttonDeleteItem'));
    await waitFor(() => expect(mocks.deleteShoppingListItem).toHaveBeenCalledWith(2));
    expect(screen.queryByText('Pasta')).not.toBeInTheDocument();
  });
});
