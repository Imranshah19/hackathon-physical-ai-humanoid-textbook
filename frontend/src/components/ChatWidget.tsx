/**
 * Floating chat widget component with toggle button and panel.
 */

import React, { useState, useCallback } from 'react';
import { ChatPanel } from './ChatPanel';

interface ChatWidgetProps {
  /** Position of the widget */
  position?: 'bottom-right' | 'bottom-left';
  /** Initial open state */
  defaultOpen?: boolean;
}

export const ChatWidget: React.FC<ChatWidgetProps> = ({
  position = 'bottom-right',
  defaultOpen = false,
}) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  const toggleOpen = useCallback(() => {
    setIsOpen((prev) => !prev);
  }, []);

  const handleClose = useCallback(() => {
    setIsOpen(false);
  }, []);

  // Get current page info
  const pageUrl = window.location.pathname;
  const pageTitle = document.title;

  return (
    <div className={`rag-widget rag-widget-${position}`}>
      {isOpen && (
        <ChatPanel
          pageUrl={pageUrl}
          pageTitle={pageTitle}
          onClose={handleClose}
        />
      )}

      <button
        className={`rag-widget-toggle ${isOpen ? 'rag-widget-toggle-open' : ''}`}
        onClick={toggleOpen}
        aria-label={isOpen ? 'Close chat' : 'Open chat'}
        aria-expanded={isOpen}
      >
        {isOpen ? (
          <CloseIcon />
        ) : (
          <ChatIcon />
        )}
      </button>
    </div>
  );
};

const ChatIcon: React.FC = () => (
  <svg
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
  </svg>
);

const CloseIcon: React.FC = () => (
  <svg
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <line x1="18" y1="6" x2="6" y2="18" />
    <line x1="6" y1="6" x2="18" y2="18" />
  </svg>
);

export default ChatWidget;
