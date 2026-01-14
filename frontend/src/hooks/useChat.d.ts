/**
 * Hook for managing chat state and interactions.
 *
 * Handles message sending, streaming, and conversation state.
 */
import { type Message, type Citation } from '../services/api';
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
export declare function useChat(options?: UseChatOptions): {
    messages: Message[];
    conversationId: string;
    isLoading: boolean;
    isStreaming: boolean;
    error: string;
    streamingContent: string;
    streamingCitations: Citation[];
    send: (message: string, context: {
        pageUrl: string;
        pageTitle?: string;
        selectedText?: string;
    }) => Promise<void>;
    rateFeedback: (messageId: string, feedback: "up" | "down") => Promise<void>;
    newConversation: () => void;
    clearError: () => void;
};
export default useChat;
//# sourceMappingURL=useChat.d.ts.map