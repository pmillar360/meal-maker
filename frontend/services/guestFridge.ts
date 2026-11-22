import { Ingredient } from './TypeService';

export const GUEST_FRIDGE_STORAGE_KEY = 'meal-maker-local-fridge-items';
export type FridgeSelection = { id?: number; name: string };

export function readGuestFridge(): FridgeSelection[] {
  const stored: unknown = JSON.parse(localStorage.getItem(GUEST_FRIDGE_STORAGE_KEY) ?? '[]');
  if (!Array.isArray(stored)) return [];
  return stored.flatMap(item => {
    if (typeof item === 'string') return [{ name: item }];
    if (item && typeof item.name === 'string') {
      return [{ name: item.name, id: Number.isInteger(item.id) && item.id > 0 ? item.id : undefined }];
    }
    return [];
  });
}

export function resolveGuestSelections(items: FridgeSelection[], catalog: Ingredient[]): FridgeSelection[] {
  const resolved = new Map<number | string, FridgeSelection>();
  for (const item of items) {
    const match = catalog.find(ingredient => matchesSelection(item, ingredient));
    const selection = match ? { id: match.id, name: match.name } : item;
    resolved.set(selection.id ?? selection.name.trim().toLowerCase(), selection);
  }
  return [...resolved.values()];
}

export function matchesSelection(item: FridgeSelection, ingredient: Ingredient) {
  if (item.id !== undefined) return item.id === ingredient.id;
  const key = item.name.trim().toLowerCase();
  return [ingredient.name, ...(ingredient.aliases ?? [])].some(name => name.trim().toLowerCase() === key);
}
