export interface Recipe {
  id: number;
  title: string;
  cooking_time: number;
  servings: number;
  meal_types?: MealType[]; // TODO Should these be optional? what difference does it make?
  diets?: Diet[]
  image_url: string;
  instructions: string;
  instructionSteps: string[];
  recipe_ingredients: RecipeIngredient[];
  description: string;
  is_featured: boolean;
  last_updated: Date;
  isFavourite?: boolean; // TODO Need to figure out how to handle this properly
}

export interface Ingredient {
  id: number;
  name: string;
  category?: string;
}

export interface RecipeIngredient {
  ingredient: Ingredient;
  quantity: string;
  unit: string;
}

export interface ShoppingListItem {
  id: number;
  name: string;
  quantity: string;
  completed?: boolean;
  category?: string;
}

export interface User {
  id: number;
  username: string;
  password: string;
}

export interface MealType {
  id: number;
  name: string;
}

export interface Diet {
  id: number;
  name: string;
}

export interface FridgeItem {
  id: number;
  name: string;
  quantity: string;
  category?: string;
}