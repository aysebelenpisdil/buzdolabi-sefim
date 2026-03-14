/**
 * Recipe Filtering Utility
 * Filters recipes based on dietary preferences, excluded ingredients, and calorie range
 */

import { RecipeWithMatch } from '../types';
import { getAllForbiddenIngredients } from './dietaryRules';
import { matchesExcludedIngredient } from './ingredientNormalizer';
import { DietaryPreferences } from './dietaryRules';

export interface CalorieRange {
    min?: number;
    max?: number;
}

/**
 * Filter recipes based on dietary preferences, excluded ingredients, and calorie range
 */
export function filterRecipes(
    recipes: RecipeWithMatch[],
    dietaryPreferences: DietaryPreferences,
    excludedIngredients: string[],
    calorieRange?: CalorieRange
): RecipeWithMatch[] {
    const forbiddenIngredients = getAllForbiddenIngredients(dietaryPreferences, excludedIngredients);

    return recipes.filter(recipe => {
        const ingredientsString = recipe.Cleaned_Ingredients || recipe.Ingredients;

        if (excludedIngredients.length > 0) {
            if (matchesExcludedIngredient(ingredientsString, excludedIngredients)) {
                return false;
            }
        }

        if (forbiddenIngredients.length > 0) {
            if (matchesExcludedIngredient(ingredientsString, forbiddenIngredients)) {
                return false;
            }
        }

        if (calorieRange && recipe.estimatedCalories != null) {
            if (calorieRange.min !== undefined && recipe.estimatedCalories < calorieRange.min) {
                return false;
            }
            if (calorieRange.max !== undefined && recipe.estimatedCalories > calorieRange.max) {
                return false;
            }
        }

        return true;
    });
}

/**
 * Get active filter labels for display
 */
export function getActiveFilterLabels(
    dietaryPreferences: DietaryPreferences,
    excludedIngredients: string[],
    calorieRange?: CalorieRange
): string[] {
    const labels: string[] = [];

    if (dietaryPreferences.vegan) labels.push('Vegan');
    if (dietaryPreferences.vegetarian && !dietaryPreferences.vegan) labels.push('Vejetaryen');
    if (dietaryPreferences.glutenFree) labels.push('Glutensiz');
    if (dietaryPreferences.dairyFree) labels.push('Süt Ürünü İçermez');
    if (dietaryPreferences.nutAllergy) labels.push('Kuruyemiş İçermez');

    if (calorieRange) {
        if (calorieRange.max !== undefined && calorieRange.max <= 400) {
            labels.push('Düşük Kalorili');
        } else if (calorieRange.min !== undefined && calorieRange.min >= 400 && calorieRange.max !== undefined && calorieRange.max <= 700) {
            labels.push('Orta Kalorili');
        } else if (calorieRange.min !== undefined && calorieRange.min > 700) {
            labels.push('Yüksek Kalorili');
        }
    }

    if (excludedIngredients.length > 0) {
        const excludedLabels = excludedIngredients.slice(0, 3).map(ing => {
            return ing.charAt(0).toUpperCase() + ing.slice(1);
        });
        if (excludedIngredients.length > 3) {
            excludedLabels.push(`+${excludedIngredients.length - 3} daha`);
        }
        labels.push(...excludedLabels.map(label => `${label} hariç`));
    }

    return labels;
}
