"use strict";
/**
 * Hook for tracking text selection in the document.
 *
 * Uses the Selection API with debouncing for performance.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.useSelection = useSelection;
const react_1 = require("react");
/**
 * Hook to track user text selection on the page.
 *
 * @param options - Configuration options
 * @returns Current selection state and clear function
 */
function useSelection(options = {}) {
    const { debounceMs = 200, minLength = 10, maxLength = 5000, } = options;
    const [selection, setSelection] = (0, react_1.useState)({
        text: '',
        isSelected: false,
    });
    const timeoutRef = (0, react_1.useRef)();
    const handleSelectionChange = (0, react_1.useCallback)(() => {
        // Clear existing timeout
        if (timeoutRef.current) {
            clearTimeout(timeoutRef.current);
        }
        // Debounce selection updates
        timeoutRef.current = setTimeout(() => {
            const sel = window.getSelection();
            const text = sel?.toString().trim() || '';
            if (text.length >= minLength) {
                setSelection({
                    text: text.slice(0, maxLength),
                    isSelected: true,
                });
            }
            else if (selection.isSelected) {
                // Keep selection until explicitly cleared or new selection
                // This prevents losing context when clicking elsewhere
            }
        }, debounceMs);
    }, [debounceMs, minLength, maxLength, selection.isSelected]);
    const clearSelection = (0, react_1.useCallback)(() => {
        setSelection({
            text: '',
            isSelected: false,
        });
        // Also clear browser selection
        window.getSelection()?.removeAllRanges();
    }, []);
    (0, react_1.useEffect)(() => {
        document.addEventListener('selectionchange', handleSelectionChange);
        return () => {
            document.removeEventListener('selectionchange', handleSelectionChange);
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }
        };
    }, [handleSelectionChange]);
    return {
        selectedText: selection.text,
        isTextSelected: selection.isSelected,
        clearSelection,
    };
}
exports.default = useSelection;
//# sourceMappingURL=useSelection.js.map