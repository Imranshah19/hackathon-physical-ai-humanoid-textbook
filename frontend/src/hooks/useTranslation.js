"use strict";
/**
 * Translation hook for chapter content.
 *
 * Provides Urdu translation functionality using the backend API.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.useTranslation = useTranslation;
const react_1 = require("react");
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
/**
 * Hook for translating text to Urdu
 */
function useTranslation() {
    const [translatedText, setTranslatedText] = (0, react_1.useState)(null);
    const [isTranslating, setIsTranslating] = (0, react_1.useState)(false);
    const [error, setError] = (0, react_1.useState)(null);
    const [isShowingTranslation, setIsShowingTranslation] = (0, react_1.useState)(false);
    const translateToUrdu = (0, react_1.useCallback)(async (text) => {
        if (!text.trim()) {
            setError('No text to translate');
            return;
        }
        setIsTranslating(true);
        setError(null);
        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/translate/urdu`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text,
                    preserve_code: true,
                }),
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || 'Translation failed');
            }
            const result = await response.json();
            setTranslatedText(result.translated);
            setIsShowingTranslation(true);
        }
        catch (err) {
            const message = err instanceof Error ? err.message : 'Translation failed';
            setError(message);
            console.error('Translation error:', err);
        }
        finally {
            setIsTranslating(false);
        }
    }, []);
    const clearTranslation = (0, react_1.useCallback)(() => {
        setTranslatedText(null);
        setError(null);
        setIsShowingTranslation(false);
    }, []);
    const toggleTranslation = (0, react_1.useCallback)(() => {
        if (translatedText) {
            setIsShowingTranslation((prev) => !prev);
        }
    }, [translatedText]);
    return {
        translatedText,
        isTranslating,
        error,
        translateToUrdu,
        clearTranslation,
        isShowingTranslation,
        toggleTranslation,
    };
}
exports.default = useTranslation;
//# sourceMappingURL=useTranslation.js.map