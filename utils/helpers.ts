import recipes from '../data/recipes';
import { Recipe, RecipeWithMatch } from '../types';

export const findSuitableRecipes = (
    userIngredients: string[]
): RecipeWithMatch[] => {
    return recipes
        .map((recipe) => {
            const recipeIngredientsLower = recipe.Ingredients.toLowerCase();
            const matchingIngredients: string[] = [];
            
            userIngredients.forEach((ingredient) => {
                if (recipeIngredientsLower.includes(ingredient.toLowerCase())) {
                    matchingIngredients.push(ingredient);
                }
            });

            return {
                ...recipe,
                matchingCount: matchingIngredients.length,
                matchingIngredients: matchingIngredients,
            };
        })
        .filter((recipe) => recipe.matchingCount > 0)
        .sort((a, b) => b.matchingCount - a.matchingCount);
};

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

export const getIngredientImageUrl = (name: string) => {
    // Assuming images are in public/images/ingredients/
    // Using simple logic to match filename. 
    return `images/ingredients/${name.toLowerCase()}.jpeg`;
};

export const getRecipeImageUrl = (imageName: string) => {
    return `images/recipies/${imageName}.jpg`;
};
