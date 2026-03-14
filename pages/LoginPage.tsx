import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../store/AuthContext';

const LoginPage: React.FC = () => {
    const { user, login, verify } = useAuth();
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();

    const [email, setEmail] = useState('');
    const [sent, setSent] = useState(false);
    const [devToken, setDevToken] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [verifying, setVerifying] = useState(false);

    useEffect(() => {
        if (user) {
            navigate('/', { replace: true });
        }
    }, [user, navigate]);

    useEffect(() => {
        const token = searchParams.get('token');
        if (token && !verifying) {
            setVerifying(true);
            verify(token)
                .then(() => navigate('/', { replace: true }))
                .catch(() => setError('Geçersiz veya süresi dolmuş bağlantı'))
                .finally(() => setVerifying(false));
        }
    }, [searchParams, verify, navigate, verifying]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setLoading(true);
        try {
            const res = await login(email);
            setSent(true);
            if (res.dev_token) {
                setDevToken(res.dev_token);
            }
        } catch {
            setError('Bir hata oluştu. Lütfen tekrar deneyin.');
        } finally {
            setLoading(false);
        }
    };

    const handleDevVerify = async () => {
        if (!devToken) return;
        setLoading(true);
        try {
            await verify(devToken);
            navigate('/', { replace: true });
        } catch {
            setError('Token doğrulanamadı.');
        } finally {
            setLoading(false);
        }
    };

    if (verifying) {
        return (
            <div className="min-h-[70vh] flex flex-col items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"></div>
                <p className="text-gray-600">Giriş doğrulanıyor...</p>
            </div>
        );
    }

    return (
        <div className="min-h-[70vh] flex items-center justify-center px-4">
            <div className="w-full max-w-md">
                <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8">
                    <div className="text-center mb-8">
                        <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center text-white font-bold text-2xl mx-auto mb-4">
                            F
                        </div>
                        <h1 className="text-2xl font-bold text-gray-900">Buzdolabı Şefi</h1>
                        <p className="mt-2 text-gray-500">E-posta adresinizle giriş yapın</p>
                    </div>

                    {!sent ? (
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                                    E-posta
                                </label>
                                <input
                                    id="email"
                                    type="email"
                                    required
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="ornek@email.com"
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-colors"
                                />
                            </div>
                            {error && (
                                <p className="text-sm text-red-600">{error}</p>
                            )}
                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full py-3 px-4 bg-primary text-white font-medium rounded-lg hover:bg-secondary transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {loading ? 'Gönderiliyor...' : 'Giriş Bağlantısı Gönder'}
                            </button>
                        </form>
                    ) : (
                        <div className="text-center space-y-4">
                            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                                </svg>
                            </div>
                            <p className="text-gray-700">
                                <span className="font-semibold">{email}</span> adresine giriş bağlantısı gönderildi.
                            </p>
                            <p className="text-sm text-gray-500">
                                E-postanızı kontrol edin ve bağlantıya tıklayın.
                            </p>

                            {devToken && (
                                <div className="mt-6 p-4 bg-amber-50 border border-amber-200 rounded-lg">
                                    <p className="text-xs font-medium text-amber-800 mb-2">Geliştirici Modu</p>
                                    <button
                                        onClick={handleDevVerify}
                                        disabled={loading}
                                        className="w-full py-2 px-4 bg-amber-600 text-white text-sm font-medium rounded-lg hover:bg-amber-700 transition-colors disabled:opacity-50"
                                    >
                                        {loading ? 'Doğrulanıyor...' : 'Hemen Giriş Yap (Dev)'}
                                    </button>
                                </div>
                            )}

                            {error && (
                                <p className="text-sm text-red-600">{error}</p>
                            )}

                            <button
                                onClick={() => { setSent(false); setDevToken(null); setError(null); }}
                                className="text-sm text-primary hover:underline"
                            >
                                Farklı e-posta kullan
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
