/**
 * Main chat panel component with input, messages, and context display.
 */

import React, { useState, useCallback } from 'react';
import { MessageList } from './MessageList';
import { ContextDisplay } from './ContextDisplay';
import { useChat } from '../hooks/useChat';
import { useSelection } from '../hooks/useSelection';

interface ChatPanelProps {
  /** Current page URL for context */
  pageUrl: string;
  /** Current page title */
  pageTitle?: string;
  /** Callback when panel is closed */
  onClose?: () => void;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({
  pageUrl,
  pageTitle,
  onClose,
}) => {
  const [inputValue, setInputValue] = useState('');

  const {
    selectedText,
    isTextSelected,
    clearSelection,
  } = useSelection();

  const {
    messages,
    isLoading,
    isStreaming,
    error,
    streamingContent,
    streamingCitations,
    send,
    rateFeedback,
    newConversation,
    clearError,
  } = useChat({ streaming: true });

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();

      if (!inputValue.trim() || isLoading) {
        return;
      }

      const message = inputValue.trim();
      setInputValue('');

      await send(message, {
        pageUrl,
        pageTitle,
        selectedText: isTextSelected ? selectedText : undefined,
      });
    },
    [inputValue, isLoading, send, pageUrl, pageTitle, isTextSelected, selectedText]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit(e);
      }
    },
    [handleSubmit]
  );

  return (
    <div className="rag-chat-panel">
      <div className="rag-chat-header">
        <h3 className="rag-chat-title">Documentation Assistant</h3>
        <div className="rag-chat-actions">
          <button
            className="rag-btn rag-btn-secondary"
            onClick={newConversation}
            title="Start new conversation"
          >
            New Chat
          </button>
          {onClose && (
            <button
              className="rag-btn rag-btn-icon"
              onClick={onClose}
              aria-label="Close chat"
            >
              ×
            </button>
          )}
        </div>
      </div>

      {isTextSelected && (
        <ContextDisplay
          selectedText={selectedText}
          onClear={clearSelection}
        />
      )}

      <MessageList
        messages={messages}
        isStreaming={isStreaming}
        streamingContent={streamingContent}
        streamingCitations={streamingCitations}
        onFeedback={rateFeedback}
      />

      {error && (
        <div className="rag-error">
          <span>{error}</span>
          <button onClick={clearError} aria-label="Dismiss error">
            ×
          </button>
        </div>
      )}

      <form className="rag-chat-input-form" onSubmit={handleSubmit}>
        <textarea
          className="rag-chat-input"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            isTextSelected
              ? 'Ask about the selected text...'
              : 'Select text and ask a question...'
          }
          rows={2}
          disabled={isLoading}
        />
        <button
          type="submit"
          className="rag-btn rag-btn-primary"
          disabled={!inputValue.trim() || isLoading}
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
};

export default ChatPanel;
