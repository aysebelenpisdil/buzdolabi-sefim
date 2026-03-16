// Helper to safely parse the python-style list string provided in the data
export const parseIngredientList = (str: string): string[] => {
    try {
        // Replace single quotes with double quotes for valid JSON,
        // assuming the data format is consistent ['a', 'b']
        // This is a basic parser for the provided data format.
        const validJson = str.replace(/'/g, '"');
        return JSON.parse(validJson);
    } catch (e) {
        console.error("Failed to parse ingredient list", str);
        return [];
    }
};

/**
 * Bir dolap malzemesinin, tarif malzemesi ihtiyacını karşılayıp karşılamadığını kontrol eder.
 * Türkçe bileşik malzeme isimlerini destekler:
 *   "domates salçası" (dolap) → "salça" (tarif) ✓  (salçası startsWith salça)
 *   "sivri biber"     (dolap) → "biber" (tarif) ✓  (biber exact word match)
 *   "mısır unu"       (dolap) → "un"    (tarif) ✓  (unu startsWith un)
 */
export const ingredientMatches = (fridgeIngredient: string, recipeIngredient: string): boolean => {
    const fridge = fridgeIngredient.toLowerCase().trim();
    const recipe = recipeIngredient.toLowerCase().trim();

    if (fridge === recipe) return true;

    // Dolaptaki malzemenin herhangi bir kelimesi, tarif malzemesiyle
    // Türkçe ek farkıyla eşleşiyor mu? (ör: salça→salçası, et→eti, un→unu)
    const fridgeWords = fridge.split(/\s+/);
    return fridgeWords.some(word =>
        word.startsWith(recipe) && word.length <= recipe.length + 3
    );
};

export interface RecipeAvailability {
    missing: string[];
    allMatching: string[];
    coveredCount: number;
    totalCount: number;
    isFullyAvailable: boolean;
}

/**
 * Bir tarifin dolaptaki malzemelerle ne kadar uyumlu olduğunu hesaplar.
 * Backend'in matchingIngredients listesini fuzzy eşleştirmeyle zenginleştirir.
 */
export const computeRecipeAvailability = (
    cleanedIngredients: string[],
    fridgeIngredients: string[],
    backendMatchingIngredients: string[]
): RecipeAvailability => {
    const missing = cleanedIngredients.filter(ing =>
        !fridgeIngredients.some(fi => ingredientMatches(fi, ing))
    );
    const seen = new Set(backendMatchingIngredients.map(m => m.toLowerCase()));
    const extra: string[] = [];
    for (const fi of fridgeIngredients) {
        if (seen.has(fi.toLowerCase())) continue;
        if (cleanedIngredients.some(ri => ingredientMatches(fi, ri))) {
            extra.push(fi);
            seen.add(fi.toLowerCase());
        }
    }
    return {
        missing,
        allMatching: [...backendMatchingIngredients, ...extra],
        coveredCount: cleanedIngredients.length - missing.length,
        totalCount: cleanedIngredients.length,
        isFullyAvailable: missing.length === 0,
    };
};

export const getRecipeImageUrl = (imageName: string) => {
    return `images/recipies/${imageName}.jpg`;
};
