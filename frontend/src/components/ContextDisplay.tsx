/**
 * Component to display the currently selected text context.
 *
 * Includes Urdu translation functionality.
 */

import React from 'react';
import { useTranslation } from '../hooks/useTranslation';

interface ContextDisplayProps {
  selectedText: string;
  onClear: () => void;
}

export const ContextDisplay: React.FC<ContextDisplayProps> = ({
  selectedText,
  onClear,
}) => {
  const {
    translatedText,
    isTranslating,
    error,
    translateToUrdu,
    clearTranslation,
    isShowingTranslation,
    toggleTranslation,
  } = useTranslation();

  if (!selectedText) {
    return null;
  }

  const displayText = isShowingTranslation && translatedText ? translatedText : selectedText;
  const truncatedText =
    displayText.length > 300
      ? displayText.slice(0, 300) + '...'
      : displayText;

  const handleTranslate = () => {
    if (translatedText) {
      toggleTranslation();
    } else {
      translateToUrdu(selectedText);
    }
  };

  const handleClear = () => {
    clearTranslation();
    onClear();
  };

  return (
    <div className="rag-context-display">
      <div className="rag-context-header">
        <span className="rag-context-label">
          {isShowingTranslation ? 'اردو ترجمہ' : 'Selected Context'}
        </span>
        <div className="rag-context-actions">
          <button
            className={`rag-context-translate ${isShowingTranslation ? 'rag-context-translate-active' : ''}`}
            onClick={handleTranslate}
            disabled={isTranslating}
            aria-label={isShowingTranslation ? 'Show original' : 'Translate to Urdu'}
            title={isShowingTranslation ? 'Show original' : 'Translate to Urdu (اردو)'}
          >
            {isTranslating ? (
              <span className="rag-translate-spinner">⟳</span>
            ) : (
              <>
                <span className="rag-translate-icon">🌐</span>
                <span className="rag-translate-label">
                  {isShowingTranslation ? 'Original' : 'اردو'}
                </span>
              </>
            )}
          </button>
          <button
            className="rag-context-clear"
            onClick={handleClear}
            aria-label="Clear selection"
          >
            ×
          </button>
        </div>
      </div>
      {error && <div className="rag-context-error">{error}</div>}
      <div
        className={`rag-context-text ${isShowingTranslation ? 'rag-context-text-urdu' : ''}`}
        dir={isShowingTranslation ? 'rtl' : 'ltr'}
        lang={isShowingTranslation ? 'ur' : 'en'}
      >
        {truncatedText}
      </div>
    </div>
  );
};

export default ContextDisplay;
