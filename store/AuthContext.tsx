import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import type { User } from '../types';
import { getCurrentUser, requestMagicLink, verifyMagicLink, logoutUser } from '../utils/api';

interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (email: string) => Promise<{ dev_token?: string }>;
    verify: (token: string) => Promise<void>;
    logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    const checkSession = useCallback(async () => {
        try {
            const session = await getCurrentUser();
            setUser(session?.user ?? null);
        } catch {
            setUser(null);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        checkSession();
    }, [checkSession]);

    const login = async (email: string) => {
        const res = await requestMagicLink(email);
        return { dev_token: res.dev_token };
    };

    const verify = async (token: string) => {
        const session = await verifyMagicLink(token);
        setUser(session.user);
    };

    const logout = async () => {
        await logoutUser();
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, verify, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
