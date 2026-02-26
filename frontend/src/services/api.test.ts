/**
 * Tests for the API service module.
 *
 * All network calls are intercepted by mocking globalThis.fetch.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { sendMessage, submitFeedback, checkHealth } from './api';
import type { ChatRequest } from './api';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function mockFetch(body: unknown, ok = true, status = 200): void {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue({
      ok,
      status,
      json: () => Promise.resolve(body),
    } as Response)
  );
}

function capturedFetchCall() {
  return (globalThis.fetch as ReturnType<typeof vi.fn>).mock.calls[0];
}

const BASE_REQUEST: ChatRequest = {
  message: 'What is ROS 2?',
  page_url: 'http://localhost:3000/docs/module-1',
};

// ---------------------------------------------------------------------------
// Session token management (localStorage)
// ---------------------------------------------------------------------------

describe('session token', () => {
  it('is created and stored in localStorage on first call', async () => {
    mockFetch({ message: {}, conversation_id: 'c1' });

    await sendMessage(BASE_REQUEST);

    const stored = localStorage.getItem('rag_chatbot_session');
    expect(stored).toBeTruthy();
    expect(typeof stored).toBe('string');
    expect(stored!.length).toBeGreaterThan(0);
  });

  it('reuses the same token across calls', async () => {
    mockFetch({ message: {}, conversation_id: 'c1' });
    await sendMessage(BASE_REQUEST);
    const token1 = localStorage.getItem('rag_chatbot_session');

    mockFetch({ message: {}, conversation_id: 'c2' });
    await sendMessage(BASE_REQUEST);
    const token2 = localStorage.getItem('rag_chatbot_session');

    expect(token1).toBe(token2);
  });

  it('sends session token in X-Session-Token header', async () => {
    mockFetch({ message: {}, conversation_id: 'c1' });

    await sendMessage(BASE_REQUEST);

    const [, options] = capturedFetchCall();
    expect((options as RequestInit).headers).toMatchObject({
      'X-Session-Token': expect.any(String),
    });
  });
});

// ---------------------------------------------------------------------------
// sendMessage()
// ---------------------------------------------------------------------------

describe('sendMessage', () => {
  it('calls the /chat endpoint with POST', async () => {
    mockFetch({ message: {}, conversation_id: 'conv-1' });

    await sendMessage(BASE_REQUEST);

    const [url, options] = capturedFetchCall();
    expect(url).toContain('/chat');
    expect((options as RequestInit).method).toBe('POST');
  });

  it('sends Content-Type: application/json', async () => {
    mockFetch({ message: {}, conversation_id: 'c1' });

    await sendMessage(BASE_REQUEST);

    const [, options] = capturedFetchCall();
    expect((options as RequestInit).headers).toMatchObject({
      'Content-Type': 'application/json',
    });
  });

  it('serialises the request body as JSON', async () => {
    mockFetch({ message: {}, conversation_id: 'c1' });

    await sendMessage(BASE_REQUEST);

    const [, options] = capturedFetchCall();
    const body = JSON.parse((options as RequestInit).body as string);
    expect(body.message).toBe('What is ROS 2?');
    expect(body.page_url).toBe('http://localhost:3000/docs/module-1');
  });

  it('includes optional fields when provided', async () => {
    mockFetch({ message: {}, conversation_id: 'c1' });

    await sendMessage({
      ...BASE_REQUEST,
      conversation_id: 'existing-conv',
      selected_text: 'some selected text',
    });

    const [, options] = capturedFetchCall();
    const body = JSON.parse((options as RequestInit).body as string);
    expect(body.conversation_id).toBe('existing-conv');
    expect(body.selected_text).toBe('some selected text');
  });

  it('returns the parsed response', async () => {
    const mockResponse = {
      message: {
        id: 'msg-1',
        role: 'assistant',
        content: 'ROS 2 is a robotics middleware.',
        citations: [],
        conversation_id: 'conv-1',
        created_at: new Date().toISOString(),
      },
      conversation_id: 'conv-1',
    };
    mockFetch(mockResponse);

    const result = await sendMessage(BASE_REQUEST);

    expect(result).toEqual(mockResponse);
  });

  it('throws when the response is not ok', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ detail: 'Internal error' }),
      } as Response)
    );

    await expect(sendMessage(BASE_REQUEST)).rejects.toThrow('Internal error');
  });

  it('throws with fallback message when error body is unreadable', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 503,
        json: () => Promise.reject(new Error('not JSON')),
      } as Response)
    );

    await expect(sendMessage(BASE_REQUEST)).rejects.toThrow('API request failed');
  });
});

// ---------------------------------------------------------------------------
// submitFeedback()
// ---------------------------------------------------------------------------

describe('submitFeedback', () => {
  it('calls the messages feedback endpoint with POST', async () => {
    mockFetch({});

    await submitFeedback('msg-123', 'up');

    const [url, options] = capturedFetchCall();
    expect(url).toContain('msg-123');
    expect(url).toContain('feedback');
    expect((options as RequestInit).method).toBe('POST');
  });

  it('sends the feedback value as a query parameter', async () => {
    mockFetch({});

    await submitFeedback('msg-456', 'down');

    const [url] = capturedFetchCall();
    expect(url).toContain('feedback=down');
  });

  it('sends "up" feedback correctly', async () => {
    mockFetch({});

    await submitFeedback('msg-789', 'up');

    const [url] = capturedFetchCall();
    expect(url).toContain('feedback=up');
  });

  it('resolves without returning a value', async () => {
    mockFetch({});

    const result = await submitFeedback('msg-123', 'up');

    expect(result).toBeUndefined();
  });
});

// ---------------------------------------------------------------------------
// checkHealth()
// ---------------------------------------------------------------------------

describe('checkHealth', () => {
  it('calls the /health endpoint', async () => {
    mockFetch({ status: 'healthy' });

    await checkHealth();

    const [url] = capturedFetchCall();
    expect(url).toContain('/health');
  });

  it('returns the health status', async () => {
    mockFetch({ status: 'healthy' });

    const result = await checkHealth();

    expect(result).toEqual({ status: 'healthy' });
  });

  it('throws when service is unavailable', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 503,
        json: () => Promise.resolve({ error: 'Service unavailable' }),
      } as Response)
    );

    await expect(checkHealth()).rejects.toThrow();
  });
});

// ---------------------------------------------------------------------------
// streamMessage() — SSE parsing
// ---------------------------------------------------------------------------

describe('streamMessage SSE parsing', () => {
  it('yields content chunks from SSE stream', async () => {
    const sse = [
      'data: {"type":"content","content":"Hello"}',
      'data: {"type":"content","content":" world"}',
      'data: {"type":"done"}',
    ].join('\n\n');

    const encoder = new TextEncoder();
    const encoded = encoder.encode(sse);

    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        body: new ReadableStream({
          start(controller) {
            controller.enqueue(encoded);
            controller.close();
          },
        }),
      } as Response)
    );

    const { streamMessage } = await import('./api');
    const chunks = [];
    for await (const chunk of streamMessage(BASE_REQUEST)) {
      chunks.push(chunk);
    }

    const contentChunks = chunks.filter((c) => c.type === 'content');
    expect(contentChunks.length).toBe(2);
    expect(contentChunks[0].content).toBe('Hello');
    expect(contentChunks[1].content).toBe(' world');
  });

  it('throws when response body is null', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        body: null,
      } as Response)
    );

    const { streamMessage } = await import('./api');

    async function collect() {
      for await (const _ of streamMessage(BASE_REQUEST)) {
        // consume
      }
    }

    await expect(collect()).rejects.toThrow('No response body');
  });

  it('throws when stream request fails', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        body: null,
      } as Response)
    );

    const { streamMessage } = await import('./api');

    async function collect() {
      for await (const _ of streamMessage(BASE_REQUEST)) {
        // consume
      }
    }

    await expect(collect()).rejects.toThrow('Stream request failed');
  });
});
