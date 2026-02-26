/**
 * Translation hook for chapter content.
 *
 * Provides Urdu translation functionality using the backend API.
 */

import { useState, useCallback } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface TranslationResult {
  original: string;
  translated: string;
  targetLanguage: string;
  targetLanguageName: string;
}

interface UseTranslationReturn {
  /** Translated text (null if not translated) */
  translatedText: string | null;
  /** Whether translation is in progress */
  isTranslating: boolean;
  /** Error message if translation failed */
  error: string | null;
  /** Translate text to Urdu */
  translateToUrdu: (text: string) => Promise<void>;
  /** Clear translation state */
  clearTranslation: () => void;
  /** Whether showing translated version */
  isShowingTranslation: boolean;
  /** Toggle between original and translated */
  toggleTranslation: () => void;
}

/**
 * Hook for translating text to Urdu
 */
export function useTranslation(): UseTranslationReturn {
  const [translatedText, setTranslatedText] = useState<string | null>(null);
  const [isTranslating, setIsTranslating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isShowingTranslation, setIsShowingTranslation] = useState(false);

  const translateToUrdu = useCallback(async (text: string) => {
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

      const result: TranslationResult = await response.json();
      setTranslatedText(result.translated);
      setIsShowingTranslation(true);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Translation failed';
      setError(message);
      console.error('Translation error:', err);
    } finally {
      setIsTranslating(false);
    }
  }, []);

  const clearTranslation = useCallback(() => {
    setTranslatedText(null);
    setError(null);
    setIsShowingTranslation(false);
  }, []);

  const toggleTranslation = useCallback(() => {
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

export default useTranslation;
