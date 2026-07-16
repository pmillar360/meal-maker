import { api } from "./apiService";
import {
  Diet,
  Ingredient,
  MealType,
  MissingIngredientsAddedResponse,
  Recipe,
  RecipeAvailabilityDetail,
  RecipeAvailabilitySummary,
} from "./TypeService";

interface FavouriteRecipeResponse {
  user_id: number;
  recipe_id: number;
}

export const getRecipes = async (
    filters: {
      ingredients?: Ingredient[];
      mealTypes?: MealType[];
      diet?: string;
    } = {}
  ): Promise<Recipe[]> => {
    const { ingredients, mealTypes: mealType, diet } = filters;
    let queryParams = new URLSearchParams();
    if (ingredients && ingredients.length > 0)
      queryParams.append(
        "ingredients",
        ingredients.map((x) => x.name).toString()
      );
    if (mealType && mealType.length > 0)
      queryParams.append(
        "meal_types",
        mealType.map((x) => x.name).toString()
      );
    if (diet) queryParams.append("diet", diet);
    const response = await api.get<Recipe[]>(`/recipes/?${queryParams}`);
    return response.data;
  };

export const getRecipesWithFridgeAvailability = async (
  filters: {
    ingredients?: Ingredient[];
    mealTypes?: MealType[];
    diet?: string;
  } = {}
): Promise<RecipeAvailabilitySummary[]> => {
  const { ingredients, mealTypes: mealType, diet } = filters;
  const queryParams = new URLSearchParams();

  if (ingredients && ingredients.length > 0) {
    queryParams.append(
      "ingredients",
      ingredients.map((x) => x.name).toString()
    );
  }

  if (mealType && mealType.length > 0) {
    queryParams.append(
      "meal_types",
      mealType.map((x) => x.name).toString()
    );
  }

  if (diet) {
    queryParams.append("diet", diet);
  }

  const response = await api.get<RecipeAvailabilitySummary[]>(
    `/recipes/with-fridge-availability/?${queryParams}`
  );
  return response.data;
};

  export const getFeaturedRecipes = async (limit: number = 10): Promise<Recipe[]> => {
    let queryParams = new URLSearchParams();
    if (limit) queryParams.append("number", limit.toString()); // Not sure if this is correct
    const response = await api.get<Recipe[]>(`/recipes/featured/?${queryParams}`);
    return response.data;
  };

  export const getRecipesByIngredients = async (ingredientNames: string[], number: number = 10): Promise<Recipe[]> => {
    let queryParams = new URLSearchParams();
    if (ingredientNames.length > 0)
      queryParams.append("ingredients", ingredientNames.toString());
    if (number) queryParams.append("number", number.toString());
    const response = await api.get<Recipe[]>(`/recipes/suggestions/?${queryParams}`);
    return response.data;
  };

  export const getRecipeById = async (id: number | string): Promise<Recipe> => {
    const response = await api.get<Recipe>(`/recipes/${id}`);
    return response.data;
  };

  export const getRecipeAvailabilityById = async (id: number | string): Promise<RecipeAvailabilityDetail> => {
    const response = await api.get<RecipeAvailabilityDetail>(`/recipes/${id}/availability/`);
    return response.data;
  };

  export const addMissingIngredientsToShoppingList = async (
    id: number | string
  ): Promise<MissingIngredientsAddedResponse> => {
    const response = await api.post<MissingIngredientsAddedResponse>(
      `/recipes/${id}/missing-to-shopping-list/`
    );
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

  export const getUserFavouriteRecipes = async (): Promise<Recipe[]> => {
    const response = await api.get<Recipe[]>("/users/me/favourites/");
    return response.data;
  };

  export const addUserFavouriteRecipe = async (recipeId: number): Promise<boolean> => {
    const response = await api.put<FavouriteRecipeResponse>(`/users/me/favourites/${recipeId}`);
    return response.data.recipe_id === recipeId;
  };

  export const removeUserFavouriteRecipe = async (recipeId: number): Promise<boolean> => {
    const response = await api.delete(`/users/me/favourites/${recipeId}`);
    return response.status === 204;
  };