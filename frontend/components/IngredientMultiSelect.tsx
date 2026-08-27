import MultiSelectAutoComplete from "./MultiSelectAutoComplete";
import { Ingredient } from "../services/TypeService";

type Props = {
  options: Ingredient[];
  selectedIngredients: Ingredient[];
  onChange: (selected: Ingredient[]) => void;
  placeholder?: string;
  containerClassName?: string;
  inputClassName?: string;
};

const toOption = (ingredient: Ingredient) => ({
  id: ingredient.id,
  label: ingredient.name,
});

export default function IngredientMultiSelect({
  options,
  selectedIngredients,
  onChange,
  placeholder,
  containerClassName,
  inputClassName,
}: Props) {
  return (
    <MultiSelectAutoComplete
      options={options.map(toOption)}
      selectedOptions={selectedIngredients.map(toOption)}
      placeholder={placeholder}
      containerClassName={containerClassName}
      inputClassName={inputClassName}
      onChange={(selected) =>
        onChange(
          selected.map((option) => ({
            id: option.id,
            name: option.label,
          }))
        )
      }
    />
  );
}
