import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../store/AuthContext';
import { deleteInteraction, getInteractionHistory, getRecipes, recordInteraction } from '../utils/api';
import type { InteractionResponse, InteractionType } from '../types';

type Tab = Extract<InteractionType, 'like' | 'skip' | 'save' | 'cook'>;

const TAB_CONFIG: { key: Tab; label: string; emptyMessage: string }[] = [
    { key: 'like', label: 'Beğendiklerim', emptyMessage: 'Henüz beğendiğiniz bir tarif yok.' },
    { key: 'skip', label: 'Atladıklarım', emptyMessage: 'Henüz atladığınız bir tarif yok.' },
    { key: 'save', label: 'Kaydettiklerim', emptyMessage: 'Henüz kaydettiğiniz bir tarif yok.' },
    { key: 'cook', label: 'Pişirdiklerim', emptyMessage: 'Henüz pişirdiğiniz bir tarif yok.' },
];

const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' });
};

const ProfilePage: React.FC = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState<Tab>('like');
    const [interactions, setInteractions] = useState<InteractionResponse[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState<string[]>([]);
    const [searchLoading, setSearchLoading] = useState(false);
    const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    useEffect(() => {
        if (!user) {
            navigate('/login');
            return;
        }
        getInteractionHistory(200, 0)
            .then(data => setInteractions(data.interactions))
            .catch(() => setError('Geçmiş yüklenemedi.'))
            .finally(() => setLoading(false));
    }, [user, navigate]);

    // Clear debounce timer on unmount
    useEffect(() => () => { if (debounceRef.current) clearTimeout(debounceRef.current); }, []);

    // Reset search when tab changes
    useEffect(() => {
        setSearchQuery('');
        setSearchResults([]);
    }, [activeTab]);

    const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const val = e.target.value;
        setSearchQuery(val);

        if (debounceRef.current) clearTimeout(debounceRef.current);

        if (!val.trim()) {
            setSearchResults([]);
            return;
        }

        debounceRef.current = setTimeout(async () => {
            setSearchLoading(true);
            try {
                const data = await getRecipes({ q: val.trim(), limit: 10 });
                setSearchResults((data.recipes as { Title: string }[]).map(r => r.Title));
            } catch {
                setSearchResults([]);
            } finally {
                setSearchLoading(false);
            }
        }, 300);
    }, []);

    const handleAddRecipe = async (title: string) => {
        try {
            await recordInteraction({ recipe_title: title, interaction_type: activeTab });
            const newItem: InteractionResponse = {
                id: Date.now(),
                recipe_title: title,
                interaction_type: activeTab,
                created_at: new Date().toISOString(),
            };
            setInteractions(prev => [newItem, ...prev]);
        } catch {
            // silently ignore
        }
        setSearchQuery('');
        setSearchResults([]);
    };

    const handleDelete = async (id: number) => {
        setInteractions(prev => prev.filter(i => i.id !== id));
        try {
            await deleteInteraction(id);
        } catch {
            // If it fails we already removed from UI; reload would restore — acceptable trade-off
        }
    };

    const filtered = useMemo(
        () => interactions.filter(i => i.interaction_type === activeTab),
        [interactions, activeTab]
    );

    return (
        <div className="max-w-2xl mx-auto px-4 py-8">
            <h1 className="text-2xl font-bold text-gray-900 mb-6">Profilim</h1>

            <div className="flex border-b border-gray-200 mb-6">
                {TAB_CONFIG.map(tab => (
                    <button
                        key={tab.key}
                        onClick={() => setActiveTab(tab.key)}
                        className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors -mb-px ${
                            activeTab === tab.key
                                ? 'border-primary text-primary'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                        }`}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Recipe search / add */}
            <div className="relative mb-4">
                <input
                    type="text"
                    value={searchQuery}
                    onChange={handleSearchChange}
                    placeholder="Tarif adı ara ve ekle..."
                    className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                />
                {searchLoading && (
                    <span className="absolute right-3 top-2.5 text-xs text-gray-400">...</span>
                )}
                {searchResults.length > 0 && (
                    <ul className="absolute z-10 mt-1 w-full bg-white border border-gray-200 rounded-md shadow-lg max-h-48 overflow-y-auto">
                        {searchResults.map(title => (
                            <li key={title}>
                                <button
                                    onClick={() => handleAddRecipe(title)}
                                    className="w-full text-left px-4 py-2 text-sm text-gray-800 hover:bg-gray-50"
                                >
                                    {title}
                                </button>
                            </li>
                        ))}
                    </ul>
                )}
            </div>

            {loading && <p className="text-gray-500 text-sm">Yükleniyor...</p>}
            {error && <p className="text-red-500 text-sm">{error}</p>}

            {!loading && !error && (
                filtered.length === 0 ? (
                    <p className="text-gray-500 text-sm">
                        {TAB_CONFIG.find(t => t.key === activeTab)?.emptyMessage}
                    </p>
                ) : (
                    <ul className="divide-y divide-gray-100">
                        {filtered.map(item => (
                            <li key={item.id} className="flex justify-between items-center py-3 group">
                                <Link
                                    to={`/recipe/${encodeURIComponent(item.recipe_title)}`}
                                    className="text-gray-800 text-sm font-medium hover:text-primary"
                                >
                                    {item.recipe_title}
                                </Link>
                                <div className="flex items-center gap-3 ml-4 shrink-0">
                                    <span className="text-xs text-gray-400">
                                        {formatDate(item.created_at)}
                                    </span>
                                    <button
                                        onClick={() => handleDelete(item.id)}
                                        className="text-gray-300 hover:text-red-400 text-sm leading-none opacity-0 group-hover:opacity-100 transition-opacity"
                                        aria-label="Sil"
                                    >
                                        ×
                                    </button>
                                </div>
                            </li>
                        ))}
                    </ul>
                )
            )}
        </div>
    );
};

export default ProfilePage;
