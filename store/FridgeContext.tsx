import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export interface DietaryPreferences {
    glutenFree: boolean;
    vegetarian: boolean;
    vegan: boolean;
    dairyFree: boolean;
    nutAllergy: boolean;
}

interface FridgeContextType {
    fridgeIngredients: string[];
    addIngredient: (ingredient: string) => void;
    removeIngredient: (ingredient: string) => void;
    dietaryPreferences: DietaryPreferences;
    setDietaryPreferences: (prefs: DietaryPreferences) => void;
    excludedIngredients: string[];
    toggleExcludedIngredient: (ingredient: string) => void;
}

const FridgeContext = createContext<FridgeContextType | undefined>(undefined);

export const FridgeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    // Initialize fridge ingredients from localStorage
    const [fridgeIngredients, setFridgeIngredients] = useState<string[]>(() => {
        const saved = localStorage.getItem('fridgeIngredients');
        return saved ? JSON.parse(saved) : [];
    });

    // Initialize dietary preferences from localStorage
    const [dietaryPreferences, setDietaryPreferencesState] = useState<DietaryPreferences>(() => {
        const saved = localStorage.getItem('dietaryPreferences');
        return saved ? JSON.parse(saved) : {
            glutenFree: false,
            vegetarian: false,
            vegan: false,
            dairyFree: false,
            nutAllergy: false
        };
    });

    // Initialize excluded ingredients from localStorage
    const [excludedIngredients, setExcludedIngredients] = useState<string[]>(() => {
        const saved = localStorage.getItem('excludedIngredients');
        return saved ? JSON.parse(saved) : [];
    });

    useEffect(() => {
        localStorage.setItem('fridgeIngredients', JSON.stringify(fridgeIngredients));
    }, [fridgeIngredients]);

    useEffect(() => {
        localStorage.setItem('dietaryPreferences', JSON.stringify(dietaryPreferences));
    }, [dietaryPreferences]);

    useEffect(() => {
        localStorage.setItem('excludedIngredients', JSON.stringify(excludedIngredients));
    }, [excludedIngredients]);

    const addIngredient = (ingredient: string) => {
        if (!fridgeIngredients.includes(ingredient)) {
            setFridgeIngredients([...fridgeIngredients, ingredient]);
        }
    };

    const removeIngredient = (ingredient: string) => {
        setFridgeIngredients(fridgeIngredients.filter(i => i !== ingredient));
    };

    const setDietaryPreferences = (prefs: DietaryPreferences) => {
        setDietaryPreferencesState(prefs);
    };

    const toggleExcludedIngredient = (ingredient: string) => {
        if (excludedIngredients.includes(ingredient)) {
            setExcludedIngredients(excludedIngredients.filter(i => i !== ingredient));
        } else {
            setExcludedIngredients([...excludedIngredients, ingredient]);
        }
    };

    return (
        <FridgeContext.Provider value={{ 
            fridgeIngredients, 
            addIngredient, 
            removeIngredient,
            dietaryPreferences,
            setDietaryPreferences,
            excludedIngredients,
            toggleExcludedIngredient
        }}>
            {children}
        </FridgeContext.Provider>
    );
};

export const useFridge = () => {
    const context = useContext(FridgeContext);
    if (!context) {
        throw new Error('useFridge must be used within a FridgeProvider');
    }
    return context;
};
