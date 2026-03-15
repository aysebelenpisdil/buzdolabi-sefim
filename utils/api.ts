import type {
    RAGRecommendRequest, RAGRecommendResponse,
    SubstitutionRequest, SubstitutionResponse,
    SessionInfo, InteractionCreate, ConsumptionCreate, UserFeatures, InteractionResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api';

export interface ApiError {
    message: string;
    status: number;
}

/**
 * Helper function to handle API errors
 */
const handleApiError = async (response: Response): Promise<never> => {
    let errorMessage = 'Bir hata oluştu';
    
    try {
        const data = await response.json();
        errorMessage = data.detail || data.message || errorMessage;
    } catch {
        errorMessage = `Sunucu hatası: ${response.status} ${response.statusText}`;
    }
    
    const error: ApiError = {
        message: errorMessage,
        status: response.status
    };
    
    throw error;
};

/**
 * Get all recipes with optional filtering
 */
export const getRecipes = async (params?: {
    ingredients?: string[];
    q?: string;
    limit?: number;
    offset?: number;
}) => {
    try {
        const queryParams = new URLSearchParams();

        if (params?.ingredients && params.ingredients.length > 0) {
            queryParams.append('ingredients', params.ingredients.join(','));
        }
        if (params?.q) {
            queryParams.append('q', params.q);
        }
        if (params?.limit) {
            queryParams.append('limit', params.limit.toString());
        }
        if (params?.offset) {
            queryParams.append('offset', params.offset.toString());
        }

        const url = `${API_BASE_URL}/recipes/?${queryParams}`;
        const response = await fetch(url, { credentials: 'include' });
        
        if (!response.ok) {
            await handleApiError(response);
        }
        
        return await response.json();
    } catch (error) {
        if ((error as ApiError).status) {
            throw error;
        }
        throw {
            message: 'Ağ hatası. Sunucunun çalıştığından emin olun.',
            status: 0
        } as ApiError;
    }
};

/**
 * Get a specific recipe by title
 */
export const getRecipeByTitle = async (title: string) => {
    try {
        const response = await fetch(
            `${API_BASE_URL}/recipes/${encodeURIComponent(title)}`,
            { credentials: 'include' }
        );
        
        if (!response.ok) {
            await handleApiError(response);
        }
        
        return await response.json();
    } catch (error) {
        if ((error as ApiError).status) {
            throw error;
        }
        throw {
            message: 'Ağ hatası. Sunucunun çalıştığından emin olun.',
            status: 0
        } as ApiError;
    }
};

/**
 * Get recipe recommendations based on ingredients
 */
export const getRecommendations = async (ingredients: string[]) => {
    try {
        const response = await fetch(`${API_BASE_URL}/recipes/recommend`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ingredients }),
        });
        
        if (!response.ok) {
            await handleApiError(response);
        }
        
        return await response.json();
    } catch (error) {
        if ((error as ApiError).status) {
            throw error;
        }
        throw {
            message: 'Ağ hatası. Sunucunun çalıştığından emin olun.',
            status: 0
        } as ApiError;
    }
};

/**
 * Get RAG-based recipe recommendations with explanations
 * 
 * Complete pipeline: Retrieve (FAISS) → Rerank (Cross-encoder) → Generate (Gemini LLM)
 * 
 * @example
 * ```typescript
 * const response = await getRAGRecommendations({
 *   ingredients: ['chicken', 'pasta', 'tomato'],
 *   preferences: { vegan: false, glutenFree: false },
 *   excluded_ingredients: ['mushroom'],
 *   explain: true,
 *   top_k: 10
 * });
 * 
 * console.log(response.recipes); // Top-k reranked recipes
 * console.log(response.explanation); // LLM-generated explanation
 * console.log(response.metadata); // Pipeline execution details
 * ```
 * 
 * @param request - RAG recommendation request with ingredients, preferences, etc.
 * @returns RAG recommendation response with recipes, explanation, and metadata
 */
export const getRAGRecommendations = async (
    request: RAGRecommendRequest
): Promise<RAGRecommendResponse> => {
    try {
        const response = await fetch(`${API_BASE_URL}/recipes/rag-recommend`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ingredients: request.ingredients,
                preferences: request.preferences,
                excluded_ingredients: request.excluded_ingredients,
                explain: request.explain ?? true,
                top_k: request.top_k ?? 10,
                retrieval_top_k: request.retrieval_top_k ?? 50,
            }),
        });
        
        if (!response.ok) {
            await handleApiError(response);
        }
        
        return await response.json();
    } catch (error) {
        if ((error as ApiError).status) {
            throw error;
        }
        throw {
            message: 'Ağ hatası. Sunucunun çalıştığından emin olun.',
            status: 0
        } as ApiError;
    }
};

/**
 * Get ingredient substitution suggestions from LLM
 */
export const getSubstitutions = async (
    request: SubstitutionRequest
): Promise<SubstitutionResponse> => {
    try {
        const response = await fetch(`${API_BASE_URL}/recipes/substitutions`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(request),
        });

        if (!response.ok) {
            await handleApiError(response);
        }

        return await response.json();
    } catch (error) {
        if ((error as ApiError).status) {
            throw error;
        }
        throw {
            message: 'Ağ hatası. Sunucunun çalıştığından emin olun.',
            status: 0
        } as ApiError;
    }
};

/**
 * Health check - test if backend is running
 */
export const checkHealth = async () => {
    try {
        const response = await fetch('http://localhost:3001/health');
        return response.ok;
    } catch {
        return false;
    }
};

// ── Auth API ──

const AUTH_BASE = API_BASE_URL.replace('/api', '');

export const requestMagicLink = async (email: string): Promise<{ message: string; dev_token?: string }> => {
    const response = await fetch(`${AUTH_BASE}/api/auth/magic-link`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
    });
    if (!response.ok) await handleApiError(response);
    return response.json();
};

export const verifyMagicLink = async (token: string): Promise<SessionInfo> => {
    const response = await fetch(`${AUTH_BASE}/api/auth/verify`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token }),
    });
    if (!response.ok) await handleApiError(response);
    return response.json();
};

export const getCurrentUser = async (): Promise<SessionInfo | null> => {
    try {
        const response = await fetch(`${AUTH_BASE}/api/auth/me`, {
            credentials: 'include',
        });
        if (response.status === 401) return null;
        if (!response.ok) return null;
        return response.json();
    } catch {
        return null;
    }
};

export const logoutUser = async (): Promise<void> => {
    await fetch(`${AUTH_BASE}/api/auth/logout`, {
        method: 'POST',
        credentials: 'include',
    });
};

// ── Feedback API ──

export const recordInteraction = async (data: InteractionCreate): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/feedback/interaction`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    if (!response.ok) {
        if (response.status === 401) {
            throw { message: 'Oturum süresi doldu. Lütfen tekrar giriş yapın.', status: 401 } as ApiError;
        }
        await handleApiError(response);
    }
};

export const logConsumption = async (data: ConsumptionCreate): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/feedback/consumption`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    if (!response.ok) {
        if (response.status === 401) {
            throw { message: 'Oturum süresi doldu. Lütfen tekrar giriş yapın.', status: 401 } as ApiError;
        }
        await handleApiError(response);
    }
};

export const getUserFeatures = async (): Promise<UserFeatures> => {
    const response = await fetch(`${API_BASE_URL}/feedback/features`, {
        credentials: 'include',
    });
    if (!response.ok) await handleApiError(response);
    return response.json();
};

export const getRecipeStatus = async (recipeTitle: string): Promise<{ status: string | null }> => {
    const response = await fetch(
        `${API_BASE_URL}/feedback/recipe-status/${encodeURIComponent(recipeTitle)}`,
        { credentials: 'include' }
    );
    if (response.status === 401) return { status: null };
    if (!response.ok) return { status: null };
    return response.json();
};

export const deleteInteraction = async (id: number): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/feedback/interaction/${id}`, {
        method: 'DELETE',
        credentials: 'include',
    });
    if (!response.ok && response.status !== 404) await handleApiError(response);
};

export const getInteractionHistory = async (
    limit = 50, offset = 0
): Promise<{ interactions: InteractionResponse[]; count: number }> => {
    const response = await fetch(
        `${API_BASE_URL}/feedback/history?limit=${limit}&offset=${offset}`,
        { credentials: 'include' }
    );
    if (!response.ok) await handleApiError(response);
    return response.json();
};
