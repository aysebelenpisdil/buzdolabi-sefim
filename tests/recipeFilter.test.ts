import { describe, it, expect } from 'vitest';
import { filterRecipes, getActiveFilterLabels } from '../utils/recipeFilter';
import type { RecipeWithMatch } from '../types';

const mockRecipe: RecipeWithMatch = {
  Title: 'Test Tarif',
  Ingredients: "['test']",
  Instructions: 'test',
  Image_Name: 'test',
  Cleaned_Ingredients: "['test']",
  matchingCount: 1,
  matchingIngredients: ['test'],
};

describe('recipeFilter', () => {
  it('filterRecipes boş tercihle tarifleri döndürür', () => {
    const result = filterRecipes(
      [mockRecipe],
      { vegan: false, vegetarian: false, glutenFree: false, dairyFree: false, nutAllergy: false },
      [],
      undefined
    );
    expect(result).toHaveLength(1);
  });

  it('getActiveFilterLabels aktif filtreleri listeler', () => {
    const labels = getActiveFilterLabels(
      { vegan: true, vegetarian: false, glutenFree: false, dairyFree: false, nutAllergy: false },
      [],
      undefined
    );
    expect(labels.some(label => label.includes('Vegan') || label.toLowerCase().includes('vegan'))).toBe(true);
  });
});
