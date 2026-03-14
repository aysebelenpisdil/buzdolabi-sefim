import React, { useState } from 'react';
import { getRecipeImageUrl } from '../utils/helpers';

interface RecipeImageProps {
    imageName: string;
    alt: string;
    className?: string;
    size?: 'card' | 'hero';
}

const PLACEHOLDER_SVG = `data:image/svg+xml,${encodeURIComponent(`
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="400" viewBox="0 0 800 400">
  <rect width="800" height="400" fill="#f3f4f6"/>
  <g transform="translate(400,170)" text-anchor="middle">
    <text font-family="system-ui,sans-serif" font-size="64" fill="#d1d5db">🍽️</text>
  </g>
  <text x="400" y="260" text-anchor="middle" font-family="system-ui,sans-serif" font-size="18" fill="#9ca3af">Görsel Yüklenemedi</text>
</svg>
`)}`;

const RecipeImage: React.FC<RecipeImageProps> = ({ imageName, alt, className = '', size = 'card' }) => {
    const [loaded, setLoaded] = useState(false);
    const [error, setError] = useState(false);

    const sizeClasses = size === 'hero'
        ? 'h-80 sm:h-96'
        : 'h-48';

    return (
        <div className={`relative w-full ${sizeClasses} overflow-hidden bg-gray-100 ${className}`}>
            {!loaded && !error && (
                <div className="absolute inset-0 animate-shimmer" />
            )}

            {error && (
                <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-100">
                    <span className="text-5xl mb-2">🍽️</span>
                    <span className="text-sm text-gray-400">Görsel Yüklenemedi</span>
                </div>
            )}

            <img
                src={error ? PLACEHOLDER_SVG : getRecipeImageUrl(imageName)}
                alt={alt}
                loading="lazy"
                onLoad={() => setLoaded(true)}
                onError={() => { if (!error) setError(true); }}
                className={`w-full h-full object-cover transition-opacity duration-500 ${loaded && !error ? 'opacity-100' : 'opacity-0'}`}
            />
        </div>
    );
};

export default RecipeImage;
