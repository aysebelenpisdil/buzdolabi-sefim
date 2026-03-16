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

export const getRecipeImageUrl = (imageName: string) => {
    return `images/recipies/${imageName}.jpg`;
};
