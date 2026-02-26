"use strict";
/**
 * Hook for managing chat state and interactions.
 *
 * Handles message sending, streaming, and conversation state.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.useChat = useChat;
const react_1 = require("react");
const api_1 = require("../services/api");
/**
 * Hook to manage chat state and interactions.
 *
 * @param options - Configuration options
 * @returns Chat state and control functions
 */
function useChat(options = {}) {
    const { streaming = true, onMessageSent, onResponseReceived, onError } = options;
    const [state, setState] = (0, react_1.useState)({
        messages: [],
        conversationId: null,
        isLoading: false,
        isStreaming: false,
        error: null,
        streamingContent: '',
        streamingCitations: [],
    });
    const abortControllerRef = (0, react_1.useRef)();
    /**
     * Send a message and get a response.
     */
    const send = (0, react_1.useCallback)(async (message, context) => {
        // Create user message object
        const userMessage = {
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
        const request = {
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
                const citations = [];
                for await (const chunk of (0, api_1.streamMessage)(request)) {
                    if (chunk.type === 'content' && chunk.content) {
                        content += chunk.content;
                        setState((prev) => ({
                            ...prev,
                            streamingContent: content,
                        }));
                    }
                    else if (chunk.type === 'citation' && chunk.citation) {
                        citations.push(chunk.citation);
                        setState((prev) => ({
                            ...prev,
                            streamingCitations: [...prev.streamingCitations, chunk.citation],
                        }));
                    }
                    else if (chunk.type === 'error') {
                        throw new Error(chunk.error);
                    }
                }
                // Create assistant message from stream
                const assistantMessage = {
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
            }
            else {
                // Sync response
                const response = await (0, api_1.sendMessage)(request);
                setState((prev) => ({
                    ...prev,
                    messages: [...prev.messages, response.message],
                    conversationId: response.conversation_id,
                    isLoading: false,
                }));
                onResponseReceived?.(response.message);
            }
        }
        catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            setState((prev) => ({
                ...prev,
                isLoading: false,
                isStreaming: false,
                error: errorMessage,
            }));
            onError?.(error instanceof Error ? error : new Error(errorMessage));
        }
    }, [state.conversationId, streaming, onMessageSent, onResponseReceived, onError]);
    /**
     * Submit feedback for a message.
     */
    const rateFeedback = (0, react_1.useCallback)(async (messageId, feedback) => {
        try {
            await (0, api_1.submitFeedback)(messageId, feedback);
            setState((prev) => ({
                ...prev,
                messages: prev.messages.map((msg) => msg.id === messageId ? { ...msg, feedback } : msg),
            }));
        }
        catch (error) {
            console.error('Failed to submit feedback:', error);
        }
    }, []);
    /**
     * Start a new conversation.
     */
    const newConversation = (0, react_1.useCallback)(() => {
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
    const clearError = (0, react_1.useCallback)(() => {
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
exports.default = useChat;
//# sourceMappingURL=useChat.js.map