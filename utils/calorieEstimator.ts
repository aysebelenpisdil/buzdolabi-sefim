import calorieData from '../src/data/calorieData.json';
import { parseIngredientList } from './helpers';

const calorieMap: Record<string, number> = calorieData;

export type CalorieLabel = 'Düşük' | 'Orta' | 'Yüksek';

/**
 * Look up the typical per-serving kcal for a single cleaned ingredient name.
 * Returns undefined when the ingredient is not in calorieData.json.
 */
export function getIngredientCalories(ingredientName: string): number | undefined {
    return calorieMap[ingredientName.toLowerCase().trim()];
}

/**
 * Estimate the total calories of a recipe from its Cleaned_Ingredients string.
 * Returns null only when *none* of the ingredients could be looked up.
 */
export function estimateRecipeCalories(cleanedIngredientsStr: string): number | null {
    const names = parseIngredientList(cleanedIngredientsStr);
    if (names.length === 0) return null;

    let total = 0;
    let matched = 0;

    for (const name of names) {
        const kcal = getIngredientCalories(name);
        if (kcal !== undefined) {
            total += kcal;
            matched++;
        }
    }

    return matched > 0 ? total : null;
}

/**
 * Classify a kcal value into a human-readable Turkish label.
 */
export function getCalorieLabel(kcal: number): CalorieLabel {
    if (kcal < 400) return 'Düşük';
    if (kcal <= 700) return 'Orta';
    return 'Yüksek';
}
