export interface Recipe {
    Title: string;
    Ingredients: string; // Stored as a stringified list in the source data
    Instructions: string;
    Image_Name: string;
    Cleaned_Ingredients: string; // Stored as a stringified list
}

export interface RecipeWithMatch extends Recipe {
    matchingCount: number;
    matchingIngredients: string[];
    estimatedCalories?: number | null;
}

export interface Ingredient {
    name: string;
}

/**
 * Dietary preferences for RAG recommendations
 */
export interface DietaryPreferences {
    vegan?: boolean;
    vegetarian?: boolean;
    glutenFree?: boolean;
    dairyFree?: boolean;
    nutAllergy?: boolean;
}

/**
 * Request model for RAG-based recommendations
 */
export interface RAGRecommendRequest {
    ingredients: string[];
    preferences?: DietaryPreferences;
    excluded_ingredients?: string[];
    explain?: boolean;
    top_k?: number;
    retrieval_top_k?: number;
}

/**
 * Metadata about RAG pipeline execution
 */
export interface RAGMetadata {
    retrieval_count: number;
    reranked_count: number;
    pipeline_stages: string[];
    retriever_used: boolean;
    reranker_used: boolean;
    llm_used: boolean;
}

/**
 * Response model for RAG-based recommendations
 */
export interface RAGRecommendResponse {
    recipes: RecipeWithMatch[];
    explanation: string | null;
    metadata: RAGMetadata;
    count: number;
}

/**
 * Request model for ingredient substitution via LLM
 */
export interface SubstitutionRequest {
    recipe_title: string;
    missing_ingredients: string[];
    available_ingredients: string[];
}

/**
 * Response model for ingredient substitution
 */
export interface SubstitutionResponse {
    substitutions: Record<string, string[]>;
    explanation: string | null;
}

// Auth types
export interface User {
    id: string;
    email: string;
    display_name: string | null;
    created_at: string;
}

export interface SessionInfo {
    user: User;
    expires_at: string;
}

// Feedback types
export type InteractionType = 'like' | 'skip' | 'view' | 'cook';
export type MealType = 'breakfast' | 'lunch' | 'dinner' | 'snack';

export interface InteractionCreate {
    recipe_title: string;
    interaction_type: InteractionType;
    context_ingredients?: string[];
}

export interface ConsumptionCreate {
    recipe_title: string;
    meal_type: MealType;
    portion_size?: number;
    rating?: number;
    notes?: string;
}

export interface UserFeatures {
    user_id: string;
    email: string;
    total_likes: number;
    total_skips: number;
    total_cooked: number;
    avg_portion: number | null;
    preferred_meal_type: string | null;
    weekly_repeat_count: number;
    like_skip_ratio: number | null;
    top_liked_recipes: string[];
    weekly_repeats: string[];
}
