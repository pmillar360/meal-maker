import { Recipe } from "../services/TypeService";

export default function MealTypeDietsChips({ recipe }: { recipe: Recipe }) {
    return (
        <div className="px-3 py-2">
            {recipe.meal_types &&
                recipe.meal_types.map((meal_type) => (
                    <span
                        key={meal_type.id}
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 mr-2"
                    >
                        {meal_type.name}
                    </span>
                ))}
            {recipe.diets &&
                recipe.diets.map((diet) => (
                    <span
                        key={diet.id}
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mr-2"
                    >
                        {diet.name}
                    </span>
                ))}
        </div>);
}