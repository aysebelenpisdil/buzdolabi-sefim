/**
 * Dietary Rules - Forbidden Ingredients by Diet Type
 * Maps dietary preferences to lists of ingredients that must be excluded
 */

export interface DietaryPreferences {
    glutenFree: boolean;
    vegetarian: boolean;
    vegan: boolean;
    dairyFree: boolean;
    nutAllergy: boolean;
}

/**
 * Get forbidden ingredients for a specific dietary preference
 */
export function getForbiddenIngredients(preferences: DietaryPreferences): string[] {
    const forbidden: Set<string> = new Set();

    // VEGAN: Hayvansal ürün yok
    if (preferences.vegan) {
        forbidden.add('kıyma');
        forbidden.add('tavuk');
        forbidden.add('dana');
        forbidden.add('kuzu');
        forbidden.add('sucuk');
        forbidden.add('pastırma');
        forbidden.add('et');
        forbidden.add('tavuk göğsü');
        forbidden.add('tavuk but');
        forbidden.add('balık');
        forbidden.add('somon');
        forbidden.add('karides');
        forbidden.add('midye');
        forbidden.add('kalamar');
        forbidden.add('ahtapot');
        forbidden.add('hamsi');
        forbidden.add('süt');
        forbidden.add('krema');
        forbidden.add('tereyağı');
        forbidden.add('peynir');
        forbidden.add('yoğurt');
        forbidden.add('yumurta');
        forbidden.add('yumurta sarısı');
        forbidden.add('yumurta akı');
        forbidden.add('mayonez');
        forbidden.add('kaşar peynir');
        forbidden.add('beyaz peynir');
        forbidden.add('sıvı krema');
        forbidden.add('bal');
        forbidden.add('jelatin');
    }

    // VEGETARIAN: Et/deniz ürünü yok
    if (preferences.vegetarian && !preferences.vegan) {
        forbidden.add('kıyma');
        forbidden.add('tavuk');
        forbidden.add('dana');
        forbidden.add('kuzu');
        forbidden.add('sucuk');
        forbidden.add('pastırma');
        forbidden.add('et');
        forbidden.add('tavuk göğsü');
        forbidden.add('tavuk but');
        forbidden.add('balık');
        forbidden.add('somon');
        forbidden.add('karides');
        forbidden.add('midye');
        forbidden.add('kalamar');
        forbidden.add('ahtapot');
        forbidden.add('hamsi');
    }

    // GLUTEN FREE: Buğday, arpa, çavdar yok
    if (preferences.glutenFree) {
        forbidden.add('un');
        forbidden.add('bulgur');
        forbidden.add('ekmek');
        forbidden.add('makarna');
        forbidden.add('irmik');
        forbidden.add('galeta unu');
        forbidden.add('yufka');
    }

    // DAIRY FREE: Süt ürünü yok
    if (preferences.dairyFree) {
        forbidden.add('süt');
        forbidden.add('krema');
        forbidden.add('tereyağı');
        forbidden.add('peynir');
        forbidden.add('yoğurt');
        forbidden.add('sıvı krema');
        forbidden.add('kaşar peynir');
        forbidden.add('beyaz peynir');
        forbidden.add('süt kreması');
    }

    // NUT ALLERGY: Kuruyemiş yok
    if (preferences.nutAllergy) {
        forbidden.add('ceviz');
        forbidden.add('fındık');
        forbidden.add('badem');
        forbidden.add('antep fıstığı');
        forbidden.add('fıstık');
        forbidden.add('çam fıstığı');
        forbidden.add('hindistan cevizi');
        forbidden.add('kırık ceviz');
    }

    return Array.from(forbidden);
}

/**
 * Get all forbidden ingredients combining dietary preferences and excluded ingredients
 */
export function getAllForbiddenIngredients(
    preferences: DietaryPreferences,
    excludedIngredients: string[]
): string[] {
    const dietaryForbidden = getForbiddenIngredients(preferences);
    const allForbidden = new Set([...dietaryForbidden, ...excludedIngredients]);
    return Array.from(allForbidden);
}

/**
 * Get active dietary preference labels
 */
export function getActiveDietaryLabels(preferences: DietaryPreferences): string[] {
    const labels: string[] = [];
    if (preferences.vegan) labels.push('Vegan');
    if (preferences.vegetarian && !preferences.vegan) labels.push('Vejetaryen');
    if (preferences.glutenFree) labels.push('Glutensiz');
    if (preferences.dairyFree) labels.push('Süt Ürünü İçermez');
    if (preferences.nutAllergy) labels.push('Kuruyemiş İçermez');
    return labels;
}





