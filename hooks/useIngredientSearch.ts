/**
 * Custom Hook: Ingredient Search with Cleaned Data
 * V3 Features: Synonyms, Fuzzy Matching, Multi-word, Recent, Popular
 * Performance: Limits results to Top 20 matches
 */

import { useMemo, useEffect, useState, useCallback } from 'react';
import cleanedIngredients from '../src/data/cleanedIngredients.json';

interface CleanedIngredient {
  name: string;
  count: number;
}

interface UseIngredientSearchOptions {
  maxResults?: number;
  minQueryLength?: number;
  enableFuzzy?: boolean;
}

interface UseIngredientSearchResult {
  suggestions: CleanedIngredient[];
  totalMatches: number;
  isSearching: boolean;
  recentIngredients: string[];
}

/**
 * Calculate Levenshtein distance for fuzzy matching
 */
function levenshteinDistance(str1: string, str2: string): number {
  const len1 = str1.length;
  const len2 = str2.length;
  const matrix: number[][] = [];

  for (let i = 0; i <= len1; i++) {
    matrix[i] = [i];
  }
  for (let j = 0; j <= len2; j++) {
    matrix[0][j] = j;
  }

  for (let i = 1; i <= len1; i++) {
    for (let j = 1; j <= len2; j++) {
      const cost = str1[i - 1] === str2[j - 1] ? 0 : 1;
      matrix[i][j] = Math.min(
        matrix[i - 1][j] + 1,
        matrix[i][j - 1] + 1,
        matrix[i - 1][j - 1] + cost
      );
    }
  }

  return matrix[len1][len2];
}

/**
 * Check if ingredient matches query (with fuzzy and synonym support)
 */
function matchesQuery(
  ingredient: CleanedIngredient,
  query: string,
  enableFuzzy: boolean
): { matches: boolean; score: number; matchType: 'exact' | 'starts' | 'contains' | 'fuzzy' | 'synonym' } {
  const name = ingredient.name.toLowerCase();
  const normalizedQuery = query.toLowerCase();

  // Exact match
  if (name === normalizedQuery) {
    return { matches: true, score: 1000, matchType: 'exact' };
  }

  // Starts with
  if (name.startsWith(normalizedQuery)) {
    return { matches: true, score: 900, matchType: 'starts' };
  }

  // Contains
  if (name.includes(normalizedQuery)) {
    return { matches: true, score: 800, matchType: 'contains' };
  }

  // Multi-word support (word order independent)
  const queryWords = normalizedQuery.split(' ').filter(w => w.length > 0);
  const nameWords = name.split(' ').filter(w => w.length > 0);
  
  if (queryWords.length > 1 && nameWords.length > 1) {
    const allWordsMatch = queryWords.every(qw => 
      nameWords.some(nw => nw.includes(qw) || qw.includes(nw))
    );
    if (allWordsMatch) {
      return { matches: true, score: 750, matchType: 'contains' };
    }
  }

  // Fuzzy matching (typo tolerance)
  if (enableFuzzy && normalizedQuery.length >= 4) {
    const distance = levenshteinDistance(normalizedQuery, name);
    const maxDistance = Math.floor(normalizedQuery.length / 3); // Allow 1 typo per 3 chars
    
    if (distance <= maxDistance) {
      return { matches: true, score: 600 - (distance * 50), matchType: 'fuzzy' };
    }

    // Check fuzzy match on individual words
    for (const word of nameWords) {
      if (word.length >= 4) {
        const wordDistance = levenshteinDistance(normalizedQuery, word);
        if (wordDistance <= maxDistance) {
          return { matches: true, score: 550 - (wordDistance * 50), matchType: 'fuzzy' };
        }
      }
    }
  }

  return { matches: false, score: 0, matchType: 'exact' };
}

/**
 * Manage recent ingredient searches
 */
const RECENT_INGREDIENTS_KEY = 'smartFridgeChef:recentIngredients';
const MAX_RECENT = 10;

function getRecentIngredients(): string[] {
  try {
    const stored = localStorage.getItem(RECENT_INGREDIENTS_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

function addRecentIngredient(ingredient: string): void {
  try {
    const recent = getRecentIngredients();
    const filtered = recent.filter(item => item !== ingredient);
    const updated = [ingredient, ...filtered].slice(0, MAX_RECENT);
    localStorage.setItem(RECENT_INGREDIENTS_KEY, JSON.stringify(updated));
  } catch {
    // Silent fail for localStorage errors
  }
}

/**
 * Advanced search with V3 features
 * @param query - Search query from user input
 * @param options - Configuration options
 * @returns Filtered ingredient suggestions with V3 enhancements
 */
export function useIngredientSearch(
  query: string,
  options: UseIngredientSearchOptions = {}
): UseIngredientSearchResult {
  const {
    maxResults = 20,
    minQueryLength = 1,
    enableFuzzy = true,
  } = options;

  const [recentIngredients, setRecentIngredients] = useState<string[]>([]);

  // Load recent ingredients on mount
  useEffect(() => {
    setRecentIngredients(getRecentIngredients());
  }, []);

  const result = useMemo(() => {
    const normalizedQuery = query.toLowerCase().trim();

    // Show popular suggestions when query is empty
    if (normalizedQuery.length === 0) {
      const popular = (cleanedIngredients as CleanedIngredient[]).slice(0, 5);
      return {
        suggestions: popular,
        totalMatches: popular.length,
        isSearching: false,
      };
    }

    // Early return for too short queries
    if (normalizedQuery.length < minQueryLength) {
      return {
        suggestions: [],
        totalMatches: 0,
        isSearching: false,
      };
    }

    // Filter and score ingredients
    const matchedIngredients = (cleanedIngredients as CleanedIngredient[])
      .map(ingredient => {
        const matchResult = matchesQuery(ingredient, normalizedQuery, enableFuzzy);
        return {
          ingredient,
          ...matchResult,
        };
      })
      .filter(item => item.matches);

    // Sort by score (higher = better) and frequency
    const sorted = matchedIngredients.sort((a, b) => {
      // Primary: Match score
      if (a.score !== b.score) {
        return b.score - a.score;
      }
      // Secondary: Frequency (recipe count)
      return b.ingredient.count - a.ingredient.count;
    });

    // Limit results for performance
    const limited = sorted.slice(0, maxResults).map(item => item.ingredient);

    return {
      suggestions: limited,
      totalMatches: matchedIngredients.length,
      isSearching: true,
    };
  }, [query, maxResults, minQueryLength, enableFuzzy]);

  return {
    ...result,
    recentIngredients,
  };
}

/**
 * Hook to track ingredient selection
 */
export function useTrackIngredient() {
  return useCallback((ingredient: string) => {
    addRecentIngredient(ingredient);
  }, []);
}


