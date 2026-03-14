/**
 * Ingredient Matching Utility
 * Provides ingredient variation matching for dietary/exclusion filtering
 */

/**
 * Get variations of an ingredient name for matching purposes.
 * Returns the normalized name itself — no map lookups needed since
 * cleanedIngredients.json already provides canonical names.
 */
export function getIngredientVariations(cleanedIngredient: string): string[] {
    const normalized = cleanedIngredient.toLowerCase().trim();
    return [normalized];
}

/**
 * Check if a recipe ingredient string matches any excluded ingredient.
 * Uses substring matching to handle compound names
 * (e.g. excluding "mantar" also catches "istiridye mantarı").
 */
export function matchesExcludedIngredient(
    recipeIngredient: string,
    excludedIngredients: string[]
): boolean {
    if (excludedIngredients.length === 0) return false;

    const recipeLower = recipeIngredient.toLowerCase();

    for (const excluded of excludedIngredients) {
        const excludedLower = excluded.toLowerCase();

        if (recipeLower === excludedLower) {
            return true;
        }

        if (recipeLower.includes(excludedLower) || excludedLower.includes(recipeLower)) {
            return true;
        }
    }

    return false;
}
