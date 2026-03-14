import React, { useState, useMemo, useEffect } from 'react';
import { useFridge } from '../store/FridgeContext';
import { checkHealth } from '../utils/api';
import { Link } from 'react-router-dom';
import { 
    getIngredientDetails, 
    groupIngredientsByCategory,
    sortCategories,
    CATEGORY_EMOJIS 
} from '../constants/ingredientData';
import { useIngredientSearch, useTrackIngredient } from '../hooks/useIngredientSearch';
import cleanedIngredients from '../src/data/cleanedIngredients.json';

const FridgePage: React.FC = () => {
    const { fridgeIngredients, addIngredient, removeIngredient } = useFridge();
    const [searchTerm, setSearchTerm] = useState('');
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');

    // V3: Advanced ingredient search with all features
    const { 
        suggestions: searchResults, 
        totalMatches,
        recentIngredients 
    } = useIngredientSearch(searchTerm, {
        maxResults: 20,
        minQueryLength: 1,
        enableFuzzy: true,
        enableSynonyms: true,
    });

    const trackIngredient = useTrackIngredient();

    // Filter out already added ingredients
    const suggestions = useMemo(() => {
        return searchResults.filter(result => 
            !fridgeIngredients.includes(result.name)
        );
    }, [searchResults, fridgeIngredients]);

    // Filter recent ingredients (exclude already added)
    const availableRecentIngredients = useMemo(() => {
        return recentIngredients.filter(name => !fridgeIngredients.includes(name));
    }, [recentIngredients, fridgeIngredients]);

    const handleAdd = (ingredientName: string) => {
        addIngredient(ingredientName);
        trackIngredient(ingredientName); // Track for recent ingredients
        setSearchTerm('');
        setIsDropdownOpen(false);
    };

    // Group ingredients by category
    const groupedIngredients = useMemo(() => {
        return groupIngredientsByCategory(fridgeIngredients);
    }, [fridgeIngredients]);

    // Sort categories: Alphabetically, but "Other" always last
    const sortedCategories = useMemo(() => {
        const categories = Object.keys(groupedIngredients);
        return sortCategories(categories);
    }, [groupedIngredients]);

    const checkBackendStatus = async () => {
        setBackendStatus('checking');
        const isOnline = await checkHealth();
        setBackendStatus(isOnline ? 'online' : 'offline');
    };

    useEffect(() => {
        checkBackendStatus();
    }, []);

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="text-center mb-10">
                <div className="flex items-center justify-center gap-2 mb-4">
                    <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl sm:tracking-tight lg:text-6xl">
                        Buzdolabınızda neler var?
                    </h1>
                    <button
                        onClick={checkBackendStatus}
                        className="ml-2 group relative"
                        title="Sunucu Durumu"
                    >
                        <span className={`inline-flex h-3 w-3 rounded-full ${
                            backendStatus === 'online' ? 'bg-green-500' :
                            backendStatus === 'offline' ? 'bg-red-500' :
                            'bg-yellow-500 animate-pulse'
                        }`}></span>
                        <span className="absolute -bottom-8 right-0 hidden group-hover:block bg-gray-800 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                            Sunucu: {backendStatus === 'online' ? 'Çevrimiçi' : backendStatus === 'offline' ? 'Çevrimdışı' : 'Kontrol ediliyor...'}
                        </span>
                    </button>
                </div>
                <p className="mt-5 max-w-xl mx-auto text-xl text-gray-500">
                    Sanal buzdolabınıza malzeme ekleyin, bugün ne pişirebileceğinizi söyleyelim.
                </p>
                {backendStatus === 'offline' && (
                    <div className="mt-4 max-w-xl mx-auto">
                        <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
                            <p className="text-sm text-yellow-800">
                                ⚠️ Sunucu çevrimdışı. Tarifler statik veriden yüklenecek. 
                                <button onClick={checkBackendStatus} className="ml-1 underline font-medium hover:text-yellow-900">
                                    Tekrar Dene
                                </button>
                            </p>
                        </div>
                    </div>
                )}
            </div>

            {/* Search Section */}
            <div className="max-w-xl mx-auto relative mb-12">
                <div className="relative">
                    <input
                        type="text"
                        className="w-full pl-12 pr-4 py-4 rounded-full border-2 border-gray-200 focus:border-primary focus:ring-0 shadow-sm text-lg outline-none transition-all"
                        placeholder="Malzeme ara (örn: 'ekmek', 'tavuk')"
                        value={searchTerm}
                        onChange={(e) => {
                            setSearchTerm(e.target.value);
                            setIsDropdownOpen(true);
                        }}
                        onFocus={() => setIsDropdownOpen(true)}
                        onBlur={() => setTimeout(() => setIsDropdownOpen(false), 200)} // Delay to allow click
                    />
                    <div className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                    </div>
                </div>

                {/* Dropdown Suggestions */}
                {isDropdownOpen && (suggestions.length > 0 || searchTerm.length === 0) && (
                    <div className="absolute z-10 w-full mt-2 bg-white rounded-xl shadow-2xl border border-gray-100 max-h-96 overflow-auto custom-scrollbar">
                        {/* Empty State: Popular & Recent */}
                        {searchTerm.length === 0 && (
                            <>
                                {/* Popular Suggestions */}
                                <div className="px-4 py-2 bg-gradient-to-r from-green-50 to-blue-50 border-b border-gray-200">
                                    <span className="text-xs font-semibold text-gray-700 flex items-center gap-1">
                                        🔥 Popüler Malzemeler
                                    </span>
                                </div>
                                {suggestions.map((ingredient) => {
                                    const details = getIngredientDetails(ingredient.name);
                                    return (
                                        <button
                                            key={`popular-${ingredient.name}`}
                                            className="w-full flex items-center px-4 py-3 hover:bg-green-50 text-left transition-colors border-b border-gray-50 group"
                                            onClick={() => handleAdd(ingredient.name)}
                                        >
                                            <div className="w-10 h-10 bg-gradient-to-br from-green-50 to-green-100 rounded-lg flex items-center justify-center mr-3 flex-shrink-0 text-2xl group-hover:scale-110 transition-transform">
                                                {details.emoji}
                                            </div>
                                            <div className="flex-1">
                                                <span className="font-medium text-gray-700 capitalize block">{details.label}</span>
                                                <div className="flex items-center gap-2">
                                                    <span className="text-xs text-gray-500">{details.category}</span>
                                                    <span className="text-xs text-gray-400">• {ingredient.count.toLocaleString()} tarif</span>
                                                </div>
                                            </div>
                                            <span className="ml-2 text-primary text-sm font-medium">+ Ekle</span>
                                        </button>
                                    );
                                })}

                                {/* Recent Ingredients */}
                                {availableRecentIngredients.length > 0 && (
                                    <>
                                        <div className="px-4 py-2 bg-gradient-to-r from-purple-50 to-pink-50 border-b border-gray-200">
                                            <span className="text-xs font-semibold text-gray-700 flex items-center gap-1">
                                                🕒 Son Kullanılanlar
                                            </span>
                                        </div>
                                        {availableRecentIngredients.slice(0, 5).map((ingredientName) => {
                                            const details = getIngredientDetails(ingredientName);
                                            // Find the ingredient in the dataset to get count
                                            const ingredientData = (cleanedIngredients as any[]).find(
                                                (ing: any) => ing.name === ingredientName
                                            );
                                            return (
                                                <button
                                                    key={`recent-${ingredientName}`}
                                                    className="w-full flex items-center px-4 py-3 hover:bg-purple-50 text-left transition-colors border-b border-gray-50 last:border-0 group"
                                                    onClick={() => handleAdd(ingredientName)}
                                                >
                                                    <div className="w-10 h-10 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg flex items-center justify-center mr-3 flex-shrink-0 text-2xl group-hover:scale-110 transition-transform">
                                                        {details.emoji}
                                                    </div>
                                                    <div className="flex-1">
                                                        <span className="font-medium text-gray-700 capitalize block">{details.label}</span>
                                                        <div className="flex items-center gap-2">
                                                            <span className="text-xs text-gray-500">{details.category}</span>
                                                            {ingredientData && (
                                                                <span className="text-xs text-gray-400">• {ingredientData.count.toLocaleString()} tarif</span>
                                                            )}
                                                        </div>
                                                    </div>
                                                    <span className="ml-2 text-purple-600 text-sm font-medium">+ Ekle</span>
                                                </button>
                                            );
                                        })}
                                    </>
                                )}
                            </>
                        )}

                        {/* Search Results */}
                        {searchTerm.length > 0 && suggestions.length > 0 && (
                            <>
                                {totalMatches > suggestions.length && (
                                    <div className="px-4 py-2 bg-gray-50 border-b border-gray-200 text-xs text-gray-600">
                                        Toplam {totalMatches} eşleşmeden {suggestions.length} tanesi gösteriliyor
                                    </div>
                                )}
                                {suggestions.map((ingredient) => {
                                    const details = getIngredientDetails(ingredient.name);
                                    return (
                                        <button
                                            key={ingredient.name}
                                            className="w-full flex items-center px-4 py-3 hover:bg-green-50 text-left transition-colors border-b border-gray-50 last:border-0 group"
                                            onClick={() => handleAdd(ingredient.name)}
                                        >
                                            <div className="w-10 h-10 bg-gradient-to-br from-green-50 to-green-100 rounded-lg flex items-center justify-center mr-3 flex-shrink-0 text-2xl group-hover:scale-110 transition-transform">
                                                {details.emoji}
                                            </div>
                                            <div className="flex-1">
                                                <span className="font-medium text-gray-700 capitalize block">{details.label}</span>
                                                <div className="flex items-center gap-2">
                                                    <span className="text-xs text-gray-500">{details.category}</span>
                                                    <span className="text-xs text-gray-400">• {ingredient.count.toLocaleString()} tarif</span>
                                                </div>
                                            </div>
                                            <span className="ml-2 text-primary text-sm font-medium">+ Ekle</span>
                                        </button>
                                    );
                                })}
                            </>
                        )}

                        {/* No Results */}
                        {searchTerm.length > 0 && suggestions.length === 0 && (
                            <div className="px-4 py-8 text-center">
                                <div className="text-4xl mb-2">🔍</div>
                                <p className="text-gray-600 font-medium">Malzeme bulunamadı</p>
                                <p className="text-xs text-gray-500 mt-1">Başka bir şey arayın</p>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Current Fridge Content - Categorized */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 sm:p-8">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold text-gray-800">Buzdolabınız</h2>
                    <span className="text-gray-500 text-sm">{fridgeIngredients.length} malzeme</span>
                </div>

                {fridgeIngredients.length === 0 ? (
                    <div className="text-center py-12 bg-gray-50 rounded-xl border border-dashed border-gray-300">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                        </svg>
                        <p className="text-gray-500">Buzdolabınız boş. Yukarıdan malzeme ekleyin!</p>
                    </div>
                ) : (
                    <div className="space-y-6">
                        {sortedCategories.map((category) => {
                            const ingredients = groupedIngredients[category];
                            const isOtherCategory = category === 'Diğer' || category.toLowerCase() === 'other' || category.toLowerCase() === 'diğer';
                            
                            return (
                                <div 
                                    key={category} 
                                    className={`bg-gradient-to-br from-gray-50 to-white rounded-xl p-4 border border-gray-100 ${
                                        isOtherCategory ? 'mt-8 pt-6 border-t-2 border-gray-300' : ''
                                    }`}
                                >
                                    {/* Category Header */}
                                    <div className="flex items-center gap-2 mb-4 pb-3 border-b border-gray-200">
                                        <span className="text-2xl">{CATEGORY_EMOJIS[category] || '🥘'}</span>
                                        <h3 className="font-semibold text-gray-800 text-lg">{category}</h3>
                                        <span className="ml-auto text-sm text-gray-500">{ingredients.length}</span>
                                    </div>
                                    
                                    {/* Ingredients in Category */}
                                    <div className="flex flex-wrap gap-2">
                                        {ingredients.map((ing) => {
                                            const details = getIngredientDetails(ing);
                                            return (
                                                <div 
                                                    key={ing} 
                                                    className="group relative bg-white border border-gray-200 rounded-lg px-3 py-2 flex items-center gap-2 hover:shadow-md hover:border-primary transition-all"
                                                >
                                                    <span className="text-xl">{details.emoji}</span>
                                                    <span className="font-medium text-gray-700 text-sm capitalize">{details.label}</span>
                                                    <button 
                                                        onClick={() => removeIngredient(ing)}
                                                        className="ml-1 text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                                                        title="Kaldır"
                                                    >
                                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                                            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                                                        </svg>
                                                    </button>
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
                
                {fridgeIngredients.length > 0 && (
                    <div className="mt-8 text-center">
                        <Link to="/recipes" className="inline-flex items-center px-8 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-primary hover:bg-secondary focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-all transform hover:scale-105">
                            Tarif Bul
                            <svg xmlns="http://www.w3.org/2000/svg" className="ml-2 h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                            </svg>
                        </Link>
                    </div>
                )}
            </div>
        </div>
    );
};

export default FridgePage;