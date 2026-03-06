const getItemName = (itemName?: string): string => {
  const trimmedName = itemName?.trim();
  return trimmedName && trimmedName.length > 0 ? trimmedName : 'item';
};

export const toastCopy = {
  favourites: {
    loadFailed: 'Could not load favourite recipes',
    added: 'Added recipe to favourites',
    updateFailed: 'Could not update favourite status',
  },
  fridge: {
    loadFailed: 'Could not load fridge ingredients',
    added: (itemName?: string) => `Added ${getItemName(itemName)} to fridge`,
    addFailed: (itemName?: string) => `Could not add ${getItemName(itemName)} to fridge`,
    removed: (itemName?: string) => `Removed ${getItemName(itemName)} from fridge`,
    removeFailed: 'Could not remove item from fridge',
  },
  shoppingList: {
    loadFailed: 'Could not load shopping list',
    added: (itemName?: string) => `Added ${getItemName(itemName)} to shopping list`,
    addFailed: (itemName?: string) => `Could not add ${getItemName(itemName)} to shopping list`,
    removed: (itemName?: string) => `Removed ${getItemName(itemName)} from shopping list`,
    removeFailed: 'Could not remove item from shopping list',
    updateFailed: 'Could not update shopping list item',
    markedComplete: (itemName?: string) => `Marked ${getItemName(itemName)} as complete`,
    markedCompleteAndAddedToFridge: (itemName?: string) =>
      `Marked ${getItemName(itemName)} as complete and added it to fridge`,
    markedCompleteFridgeAddFailed: (itemName?: string) =>
      `Marked ${getItemName(itemName)} as complete, but could not add it to fridge`,
    movedBackToActive: (itemName?: string) => `Moved ${getItemName(itemName)} back to active list`,
  },
};
