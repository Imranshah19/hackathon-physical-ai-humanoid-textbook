/**
 * Component to render the list of chat messages.
 */

import React from 'react';
import type { Message, Citation } from '../services/api';
import { CitationList } from './CitationLink';

interface MessageItemProps {
  message: Message;
  onFeedback?: (messageId: string, feedback: 'up' | 'down') => void;
}

const MessageItem: React.FC<MessageItemProps> = ({ message, onFeedback }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`rag-message ${isUser ? 'rag-message-user' : 'rag-message-assistant'}`}>
      <div className="rag-message-content">
        {message.content}
      </div>

      {!isUser && message.citations.length > 0 && (
        <CitationList citations={message.citations} />
      )}

      {!isUser && onFeedback && (
        <div className="rag-message-feedback">
          <button
            className={`rag-feedback-btn ${message.feedback === 'up' ? 'active' : ''}`}
            onClick={() => onFeedback(message.id, 'up')}
            aria-label="Helpful"
          >
            👍
          </button>
          <button
            className={`rag-feedback-btn ${message.feedback === 'down' ? 'active' : ''}`}
            onClick={() => onFeedback(message.id, 'down')}
            aria-label="Not helpful"
          >
            👎
          </button>
        </div>
      )}
    </div>
  );
};

interface StreamingMessageProps {
  content: string;
  citations: Citation[];
}

const StreamingMessage: React.FC<StreamingMessageProps> = ({
  content,
  citations,
}) => {
  return (
    <div className="rag-message rag-message-assistant rag-message-streaming">
      <div className="rag-message-content">
        {content}
        <span className="rag-typing-indicator">▊</span>
      </div>
      {citations.length > 0 && <CitationList citations={citations} />}
    </div>
  );
};

interface MessageListProps {
  messages: Message[];
  isStreaming: boolean;
  streamingContent: string;
  streamingCitations: Citation[];
  onFeedback?: (messageId: string, feedback: 'up' | 'down') => void;
}

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  isStreaming,
  streamingContent,
  streamingCitations,
  onFeedback,
}) => {
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  if (messages.length === 0 && !isStreaming) {
    return (
      <div className="rag-messages-empty">
        <p>Select text from the documentation and ask a question about it.</p>
      </div>
    );
  }

  return (
    <div className="rag-messages">
      {messages.map((message) => (
        <MessageItem
          key={message.id}
          message={message}
          onFeedback={onFeedback}
        />
      ))}

      {isStreaming && (
        <StreamingMessage
          content={streamingContent}
          citations={streamingCitations}
        />
      )}

      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;
