import { api } from "./apiService";
import { Diet, Ingredient, MealType, Recipe } from "./TypeService";

export const getRecipes = async (
    filters: {
      ingredients?: Ingredient[];
      mealType?: string;
      diet?: string;
    } = {}
  ): Promise<Recipe[]> => {
    const { ingredients, mealType, diet } = filters;
    let queryParams = new URLSearchParams();
    if (ingredients && ingredients.length > 0)
      queryParams.append(
        "ingredients",
        ingredients.map((x) => x.name).toString()
      );
    if (mealType) queryParams.append("meal_type", mealType);
    if (diet) queryParams.append("diet", diet);
    const response = await api.get<Recipe[]>(`/recipes/?${queryParams}`);
    return response.data;
  };

  export const getFeaturedRecipes = async (limit: number = 10): Promise<Recipe[]> => {
    let queryParams = new URLSearchParams();
    if (limit) queryParams.append("number", limit.toString()); // Not sure if this is correct
    const response = await api.get<Recipe[]>(`/recipes/featured/?${queryParams}`);
    return response.data;
  };

  export const getRecipeById = async (id: number | string): Promise<Recipe> => {
    const response = await api.get<Recipe>(`/recipes/${id}`);
    return response.data;
  };

  // TODO Maybe all "getAll" methods should implement a limit or pagination features
  export const getAllIngredients = async (): Promise<Ingredient[]> => {
    const response = await api.get<Ingredient[]>("/ingredients/");
    return response.data;
  };

  export const getAllMealTypes = async (): Promise<MealType[]> => {
    const response = await api.get<MealType[]>("/meal-types/");
    return response.data;
  };

  export const getAllDiets = async (): Promise<Diet[]> => {
    const response = await api.get<Diet[]>("/diets/");
    return response.data;
  };