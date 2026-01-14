/**
 * API client service for the RAG chatbot backend.
 *
 * Handles HTTP requests and SSE streaming.
 */
export interface Citation {
    text: string;
    source_url: string;
    section_title?: string;
    relevance: number;
}
export interface Message {
    id: string;
    conversation_id: string;
    role: 'user' | 'assistant';
    content: string;
    citations: Citation[];
    tokens_used?: number;
    latency_ms?: number;
    feedback?: 'up' | 'down';
    created_at: string;
}
export interface ChatRequest {
    message: string;
    conversation_id?: string;
    page_url: string;
    page_title?: string;
    selected_text?: string;
}
export interface ChatResponse {
    message: Message;
    conversation_id: string;
}
export interface StreamChunk {
    type: 'content' | 'citation' | 'done' | 'error';
    content?: string;
    citation?: Citation;
    message_id?: string;
    error?: string;
}
/**
 * Send a chat message and get a complete response.
 */
export declare function sendMessage(request: ChatRequest): Promise<ChatResponse>;
/**
 * Send a chat message and stream the response.
 */
export declare function streamMessage(request: ChatRequest): AsyncGenerator<StreamChunk, void, unknown>;
/**
 * Submit feedback for a message.
 */
export declare function submitFeedback(messageId: string, feedback: 'up' | 'down'): Promise<void>;
/**
 * Check API health.
 */
export declare function checkHealth(): Promise<{
    status: string;
}>;
//# sourceMappingURL=api.d.ts.map