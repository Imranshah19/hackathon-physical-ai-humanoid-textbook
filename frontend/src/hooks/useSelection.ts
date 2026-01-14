/**
 * Hook for tracking text selection in the document.
 *
 * Uses the Selection API with debouncing for performance.
 */

import { useState, useEffect, useCallback, useRef } from 'react';

interface SelectionState {
  text: string;
  isSelected: boolean;
}

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
export function useSelection(options: UseSelectionOptions = {}) {
  const {
    debounceMs = 200,
    minLength = 10,
    maxLength = 5000,
  } = options;

  const [selection, setSelection] = useState<SelectionState>({
    text: '',
    isSelected: false,
  });

  const timeoutRef = useRef<ReturnType<typeof setTimeout>>();

  const handleSelectionChange = useCallback(() => {
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
      } else if (selection.isSelected) {
        // Keep selection until explicitly cleared or new selection
        // This prevents losing context when clicking elsewhere
      }
    }, debounceMs);
  }, [debounceMs, minLength, maxLength, selection.isSelected]);

  const clearSelection = useCallback(() => {
    setSelection({
      text: '',
      isSelected: false,
    });
    // Also clear browser selection
    window.getSelection()?.removeAllRanges();
  }, []);

  useEffect(() => {
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

export default useSelection;
