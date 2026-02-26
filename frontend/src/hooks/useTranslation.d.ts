/**
 * Translation hook for chapter content.
 *
 * Provides Urdu translation functionality using the backend API.
 */
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
export declare function useTranslation(): UseTranslationReturn;
export default useTranslation;
//# sourceMappingURL=useTranslation.d.ts.map