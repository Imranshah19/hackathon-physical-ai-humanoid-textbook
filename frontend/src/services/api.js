"use strict";
/**
 * API client service for the RAG chatbot backend.
 *
 * Handles HTTP requests and SSE streaming.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.sendMessage = sendMessage;
exports.streamMessage = streamMessage;
exports.submitFeedback = submitFeedback;
exports.checkHealth = checkHealth;
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const SESSION_KEY = 'rag_chatbot_session';
/**
 * Get or create session token.
 */
function getSessionToken() {
    let token = localStorage.getItem(SESSION_KEY);
    if (!token) {
        token = crypto.randomUUID().replace(/-/g, '') + crypto.randomUUID().replace(/-/g, '');
        localStorage.setItem(SESSION_KEY, token);
    }
    return token;
}
/**
 * Make an authenticated API request.
 */
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
        'X-Session-Token': getSessionToken(),
        ...options.headers,
    };
    const response = await fetch(url, {
        ...options,
        headers,
    });
    if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(error.detail || error.error || 'API request failed');
    }
    return response.json();
}
/**
 * Send a chat message and get a complete response.
 */
async function sendMessage(request) {
    return apiRequest('/chat', {
        method: 'POST',
        body: JSON.stringify(request),
    });
}
/**
 * Send a chat message and stream the response.
 */
async function* streamMessage(request) {
    const url = `${API_BASE_URL}/chat/stream`;
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Session-Token': getSessionToken(),
        },
        body: JSON.stringify(request),
    });
    if (!response.ok) {
        throw new Error('Stream request failed');
    }
    const reader = response.body?.getReader();
    if (!reader) {
        throw new Error('No response body');
    }
    const decoder = new TextDecoder();
    let buffer = '';
    try {
        while (true) {
            const { done, value } = await reader.read();
            if (done)
                break;
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n\n');
            buffer = lines.pop() || '';
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    try {
                        const chunk = JSON.parse(data);
                        yield chunk;
                        if (chunk.type === 'done' || chunk.type === 'error') {
                            return;
                        }
                    }
                    catch {
                        console.error('Failed to parse SSE data:', data);
                    }
                }
            }
        }
    }
    finally {
        reader.releaseLock();
    }
}
/**
 * Submit feedback for a message.
 */
async function submitFeedback(messageId, feedback) {
    await apiRequest(`/messages/${messageId}/feedback?feedback=${feedback}`, {
        method: 'POST',
    });
}
/**
 * Check API health.
 */
async function checkHealth() {
    return apiRequest('/health');
}
//# sourceMappingURL=api.js.map