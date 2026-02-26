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

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const SESSION_KEY = 'rag_chatbot_session';

/**
 * Get or create session token.
 */
function getSessionToken(): string {
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
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    'X-Session-Token': getSessionToken(),
    ...options.headers,
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || error.error || 'API request failed');
  }

  return response.json();
}

/**
 * Send a chat message and get a complete response.
 */
export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  return apiRequest<ChatResponse>('/chat', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

/**
 * Send a chat message and stream the response.
 */
export async function* streamMessage(
  request: ChatRequest
): AsyncGenerator<StreamChunk, void, unknown> {
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

  if (!response.body) {
    throw new Error('No response body');
  }
  const reader = response.body.getReader();

  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          try {
            const chunk: StreamChunk = JSON.parse(data);
            yield chunk;
            if (chunk.type === 'done' || chunk.type === 'error') {
              return;
            }
          } catch {
            console.error('Failed to parse SSE data:', data);
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

/**
 * Submit feedback for a message.
 */
export async function submitFeedback(
  messageId: string,
  feedback: 'up' | 'down'
): Promise<void> {
  await apiRequest(`/messages/${messageId}/feedback?feedback=${feedback}`, {
    method: 'POST',
  });
}

/**
 * Check API health.
 */
export async function checkHealth(): Promise<{ status: string }> {
  return apiRequest('/health');
}
