/**
 * Hook for tracking text selection in the document.
 *
 * Uses the Selection API with debouncing for performance.
 */
interface UseSelectionOptions {
    /** Debounce delay in milliseconds */
    debounceMs?: number;
    /** Minimum text length to consider as selection */
    minLength?: number;
    /** Maximum text length to capture */
    maxLength?: number;
}
/**
 * Hook to track user text selection on the page.
 *
 * @param options - Configuration options
 * @returns Current selection state and clear function
 */
export declare function useSelection(options?: UseSelectionOptions): {
    selectedText: string;
    isTextSelected: boolean;
    clearSelection: () => void;
};
export default useSelection;
//# sourceMappingURL=useSelection.d.ts.map