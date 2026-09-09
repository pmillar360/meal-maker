import { expect, Page, test } from '@playwright/test';

const recipeCards = (page: Page) => page.locator('a[href^="/recipes/"]');

async function chooseAutocompleteOption(
  page: Page,
  container: ReturnType<Page['locator']>,
  value: string,
) {
  await container.locator('input').fill(value);
  await container.getByText(value, { exact: true }).click();
}

async function register(page: Page) {
  const username = `e2e-${Date.now()}-${Math.random().toString(36).slice(2)}`;
  await page.getByPlaceholder('Username').fill(username);
  await page.getByPlaceholder('Password').fill('playwright-password');
  await page.getByRole('button', { name: 'Register' }).click();
  await expect(page.getByText(username, { exact: true })).toBeVisible();
}

test('a guest can enter an on-hand ingredient and get matching recipes', async ({ page }) => {
  await page.goto('/');

  const ingredientSearch = page.getByPlaceholder('Try eggs, spinach, onion...');
  await ingredientSearch.fill('Tomato');
  await page.getByText('Tomato', { exact: true }).click();

  await expect(page.getByRole('button', { name: 'Tomato ×' })).toBeVisible();
  await expect(recipeCards(page).filter({ hasText: 'Tomato Pasta' })).toBeVisible();
  await expect(page.getByText('1/2 ingredients available').first()).toBeVisible();
  await expect
    .poll(() => page.evaluate(() => localStorage.getItem('meal-maker-local-fridge-items')))
    .toContain('Tomato');
});

test('recipes can be filtered by ingredient, meal type, and diet', async ({ page }) => {
  await page.goto('/recipes');
  await expect(recipeCards(page)).toHaveCount(6);

  const ingredientFilter = page.getByText('Ingredients:', { exact: true }).locator('..');
  await chooseAutocompleteOption(page, ingredientFilter, 'Tomato');
  await expect(recipeCards(page)).toHaveCount(5);
  await expect(recipeCards(page).filter({ hasText: 'Apple Snack' })).toHaveCount(0);

  await page.getByRole('button', { name: 'Clear Filters' }).click();
  const mealTypeFilter = page.getByText('Meal Type:', { exact: true }).locator('..');
  for (const [mealType, recipe] of [
    ['Breakfast', 'Breakfast Omelette'],
    ['Lunch', 'Chicken Lunch Bowl'],
    ['Dinner', 'Tomato Pasta'],
    ['Snack', 'Apple Snack'],
  ] as const) {
    await chooseAutocompleteOption(page, mealTypeFilter, mealType);
    await expect(recipeCards(page)).toHaveCount(1);
    await expect(recipeCards(page).filter({ hasText: recipe })).toBeVisible();
    await page.getByRole('button', { name: 'Clear Filters' }).click();
  }

  for (const [diet, expectedCount, recipe] of [
    ['Vegetarian', 3, 'Breakfast Omelette'],
    ['Vegan', 3, 'Apple Snack'],
    ['High-Protein', 2, 'Chicken Lunch Bowl'],
  ] as const) {
    await page.getByLabel('Diet Type:').selectOption(diet);
    await expect(recipeCards(page)).toHaveCount(expectedCount);
    await expect(recipeCards(page).filter({ hasText: recipe })).toBeVisible();
  }
});

test('recipe details show ingredients, cooking time, and servings', async ({ page }) => {
  await page.goto('/recipes/1');

  await expect(page.getByRole('heading', { name: 'Tomato Pasta' })).toBeVisible();
  await expect(page.getByText('20 minutes')).toBeVisible();
  await expect(page.getByText('Servings: 2')).toBeVisible();
  await expect(page.getByRole('cell', { name: 'Tomato', exact: true })).toBeVisible();
  await expect(page.getByRole('cell', { name: 'Pasta', exact: true })).toBeVisible();
});

test('missing ingredients generate a shopping list that can be updated and deleted', async ({ page }) => {
  await page.goto('/');
  await register(page);

  const ingredientSearch = page.getByPlaceholder('Try eggs, spinach, onion...');
  await ingredientSearch.fill('Tomato');
  await page.getByText('Tomato', { exact: true }).click();
  await expect(page.getByRole('button', { name: 'Tomato ×' })).toBeVisible();

  await page.goto('/recipes/1');
  await expect(page.getByText('In Fridge', { exact: true })).toBeVisible();
  await expect(page.getByText('Missing', { exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Add All Missing to Shopping List' }).click();
  await expect(page.getByText('Added 1 missing ingredient(s) to your shopping list.')).toBeVisible();

  await page.getByRole('link', { name: 'Shopping List' }).click();
  await expect(page.getByText('Pasta', { exact: true })).toBeVisible();

  const quantity = page.getByPlaceholder('Add quantity');
  await quantity.fill('500 g');
  await expect(quantity).toHaveValue('500 g');

  await page.getByTitle('buttonToggleComplete').click();
  await expect(page.getByRole('heading', { name: 'Completed items' })).toBeVisible();
  await page.getByTitle('buttonDeleteItem').click();
  await expect(page.getByText('Your shopping list is empty')).toBeVisible();
});
