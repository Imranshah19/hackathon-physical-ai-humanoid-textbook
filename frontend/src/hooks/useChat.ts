/**
 * Hook for managing chat state and interactions.
 *
 * Handles message sending, streaming, and conversation state.
 */

import { useState, useCallback, useRef } from 'react';
import {
  sendMessage,
  streamMessage,
  submitFeedback,
  type Message,
  type Citation,
  type ChatRequest,
} from '../services/api';

interface ChatState {
  messages: Message[];
  conversationId: string | null;
  isLoading: boolean;
  isStreaming: boolean;
  error: string | null;
  streamingContent: string;
  streamingCitations: Citation[];
}

interface UseChatOptions {
  /** Use streaming responses */
  streaming?: boolean;
  /** Callback when message is sent */
  onMessageSent?: (message: Message) => void;
  /** Callback when response is received */
  onResponseReceived?: (message: Message) => void;
  /** Callback on error */
  onError?: (error: Error) => void;
}

/**
 * Hook to manage chat state and interactions.
 *
 * @param options - Configuration options
 * @returns Chat state and control functions
 */
export function useChat(options: UseChatOptions = {}) {
  const { streaming = true, onMessageSent, onResponseReceived, onError } = options;

  const [state, setState] = useState<ChatState>({
    messages: [],
    conversationId: null,
    isLoading: false,
    isStreaming: false,
    error: null,
    streamingContent: '',
    streamingCitations: [],
  });

  const abortControllerRef = useRef<AbortController>();

  /**
   * Send a message and get a response.
   */
  const send = useCallback(
    async (
      message: string,
      context: {
        pageUrl: string;
        pageTitle?: string;
        selectedText?: string;
      }
    ) => {
      // Create user message object
      const userMessage: Message = {
        id: crypto.randomUUID(),
        conversation_id: state.conversationId || '',
        role: 'user',
        content: message,
        citations: [],
        created_at: new Date().toISOString(),
      };

      // Update state with user message
      setState((prev) => ({
        ...prev,
        messages: [...prev.messages, userMessage],
        isLoading: true,
        isStreaming: streaming,
        error: null,
        streamingContent: '',
        streamingCitations: [],
      }));

      onMessageSent?.(userMessage);

      const request: ChatRequest = {
        message,
        conversation_id: state.conversationId || undefined,
        page_url: context.pageUrl,
        page_title: context.pageTitle,
        selected_text: context.selectedText,
      };

      try {
        if (streaming) {
          // Stream response
          let content = '';
          const citations: Citation[] = [];

          for await (const chunk of streamMessage(request)) {
            if (chunk.type === 'content' && chunk.content) {
              content += chunk.content;
              setState((prev) => ({
                ...prev,
                streamingContent: content,
              }));
            } else if (chunk.type === 'citation' && chunk.citation) {
              citations.push(chunk.citation);
              setState((prev) => ({
                ...prev,
                streamingCitations: [...prev.streamingCitations, chunk.citation!],
              }));
            } else if (chunk.type === 'error') {
              throw new Error(chunk.error);
            }
          }

          // Create assistant message from stream
          const assistantMessage: Message = {
            id: crypto.randomUUID(),
            conversation_id: state.conversationId || '',
            role: 'assistant',
            content,
            citations,
            created_at: new Date().toISOString(),
          };

          setState((prev) => ({
            ...prev,
            messages: [...prev.messages, assistantMessage],
            isLoading: false,
            isStreaming: false,
            streamingContent: '',
            streamingCitations: [],
          }));

          onResponseReceived?.(assistantMessage);
        } else {
          // Sync response
          const response = await sendMessage(request);

          setState((prev) => ({
            ...prev,
            messages: [...prev.messages, response.message],
            conversationId: response.conversation_id,
            isLoading: false,
          }));

          onResponseReceived?.(response.message);
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        setState((prev) => ({
          ...prev,
          isLoading: false,
          isStreaming: false,
          error: errorMessage,
        }));
        onError?.(error instanceof Error ? error : new Error(errorMessage));
      }
    },
    [state.conversationId, streaming, onMessageSent, onResponseReceived, onError]
  );

  /**
   * Submit feedback for a message.
   */
  const rateFeedback = useCallback(
    async (messageId: string, feedback: 'up' | 'down') => {
      try {
        await submitFeedback(messageId, feedback);
        setState((prev) => ({
          ...prev,
          messages: prev.messages.map((msg) =>
            msg.id === messageId ? { ...msg, feedback } : msg
          ),
        }));
      } catch (error) {
        console.error('Failed to submit feedback:', error);
      }
    },
    []
  );

  /**
   * Start a new conversation.
   */
  const newConversation = useCallback(() => {
    setState({
      messages: [],
      conversationId: null,
      isLoading: false,
      isStreaming: false,
      error: null,
      streamingContent: '',
      streamingCitations: [],
    });
  }, []);

  /**
   * Clear error state.
   */
  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  return {
    messages: state.messages,
    conversationId: state.conversationId,
    isLoading: state.isLoading,
    isStreaming: state.isStreaming,
    error: state.error,
    streamingContent: state.streamingContent,
    streamingCitations: state.streamingCitations,
    send,
    rateFeedback,
    newConversation,
    clearError,
  };
}

export default useChat;
