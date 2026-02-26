/**
 * Tests for the useChat hook.
 *
 * Uses @testing-library/react renderHook to exercise the hook in isolation,
 * with the API module mocked so no real network calls are made.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useChat } from './useChat';

// ---------------------------------------------------------------------------
// Mock the API module
// ---------------------------------------------------------------------------

vi.mock('../services/api', () => ({
  sendMessage: vi.fn(),
  streamMessage: vi.fn(),
  submitFeedback: vi.fn(),
}));

import * as api from '../services/api';

const mockSendMessage = vi.mocked(api.sendMessage);
const mockSubmitFeedback = vi.mocked(api.submitFeedback);
const mockStreamMessage = vi.mocked(api.streamMessage);

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const PAGE_CTX = { pageUrl: 'http://localhost:3000/docs', pageTitle: 'Docs' };

function makeAssistantMessage(overrides = {}) {
  return {
    id: 'assistant-msg-1',
    conversation_id: 'conv-1',
    role: 'assistant' as const,
    content: 'That is a great question!',
    citations: [],
    created_at: new Date().toISOString(),
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Initial state
// ---------------------------------------------------------------------------

describe('useChat initial state', () => {
  it('starts with an empty messages array', () => {
    const { result } = renderHook(() => useChat({ streaming: false }));
    expect(result.current.messages).toEqual([]);
  });

  it('starts with null conversationId', () => {
    const { result } = renderHook(() => useChat({ streaming: false }));
    expect(result.current.conversationId).toBeNull();
  });

  it('starts with isLoading false', () => {
    const { result } = renderHook(() => useChat({ streaming: false }));
    expect(result.current.isLoading).toBe(false);
  });

  it('starts with isStreaming false', () => {
    const { result } = renderHook(() => useChat({ streaming: false }));
    expect(result.current.isStreaming).toBe(false);
  });

  it('starts with null error', () => {
    const { result } = renderHook(() => useChat({ streaming: false }));
    expect(result.current.error).toBeNull();
  });

  it('starts with empty streamingContent', () => {
    const { result } = renderHook(() => useChat({ streaming: false }));
    expect(result.current.streamingContent).toBe('');
  });

  it('exposes send, rateFeedback, newConversation, clearError functions', () => {
    const { result } = renderHook(() => useChat({ streaming: false }));
    expect(typeof result.current.send).toBe('function');
    expect(typeof result.current.rateFeedback).toBe('function');
    expect(typeof result.current.newConversation).toBe('function');
    expect(typeof result.current.clearError).toBe('function');
  });
});

// ---------------------------------------------------------------------------
// send() — non-streaming mode
// ---------------------------------------------------------------------------

describe('useChat send() (non-streaming)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('adds user message to messages immediately', async () => {
    const assistantMsg = makeAssistantMessage();
    mockSendMessage.mockResolvedValue({
      message: assistantMsg,
      conversation_id: 'conv-1',
    });

    const { result } = renderHook(() => useChat({ streaming: false }));

    await act(async () => {
      await result.current.send('Hello', PAGE_CTX);
    });

    const userMsg = result.current.messages.find((m) => m.role === 'user');
    expect(userMsg).toBeDefined();
    expect(userMsg!.content).toBe('Hello');
  });

  it('adds assistant response to messages after send', async () => {
    const assistantMsg = makeAssistantMessage({ content: 'ROS 2 answer' });
    mockSendMessage.mockResolvedValue({
      message: assistantMsg,
      conversation_id: 'conv-1',
    });

    const { result } = renderHook(() => useChat({ streaming: false }));

    await act(async () => {
      await result.current.send('What is ROS 2?', PAGE_CTX);
    });

    const messages = result.current.messages;
    expect(messages).toHaveLength(2);
    expect(messages[0].role).toBe('user');
    expect(messages[1].role).toBe('assistant');
    expect(messages[1].content).toBe('ROS 2 answer');
  });

  it('updates conversationId from response', async () => {
    mockSendMessage.mockResolvedValue({
      message: makeAssistantMessage(),
      conversation_id: 'new-conv-id',
    });

    const { result } = renderHook(() => useChat({ streaming: false }));

    await act(async () => {
      await result.current.send('Hello', PAGE_CTX);
    });

    expect(result.current.conversationId).toBe('new-conv-id');
  });

  it('sets error when send fails', async () => {
    mockSendMessage.mockRejectedValue(new Error('Network error'));

    const { result } = renderHook(() => useChat({ streaming: false }));

    await act(async () => {
      await result.current.send('Hello', PAGE_CTX);
    });

    expect(result.current.error).toBe('Network error');
    expect(result.current.isLoading).toBe(false);
  });

  it('calls onMessageSent callback with user message', async () => {
    mockSendMessage.mockResolvedValue({
      message: makeAssistantMessage(),
      conversation_id: 'c1',
    });

    const onMessageSent = vi.fn();
    const { result } = renderHook(() => useChat({ streaming: false, onMessageSent }));

    await act(async () => {
      await result.current.send('Hello', PAGE_CTX);
    });

    expect(onMessageSent).toHaveBeenCalledOnce();
    expect(onMessageSent.mock.calls[0][0].content).toBe('Hello');
    expect(onMessageSent.mock.calls[0][0].role).toBe('user');
  });

  it('calls onResponseReceived callback with assistant message', async () => {
    const assistantMsg = makeAssistantMessage();
    mockSendMessage.mockResolvedValue({
      message: assistantMsg,
      conversation_id: 'c1',
    });

    const onResponseReceived = vi.fn();
    const { result } = renderHook(() => useChat({ streaming: false, onResponseReceived }));

    await act(async () => {
      await result.current.send('Hello', PAGE_CTX);
    });

    expect(onResponseReceived).toHaveBeenCalledWith(assistantMsg);
  });

  it('calls onError callback when send fails', async () => {
    mockSendMessage.mockRejectedValue(new Error('Boom'));

    const onError = vi.fn();
    const { result } = renderHook(() => useChat({ streaming: false, onError }));

    await act(async () => {
      await result.current.send('Hello', PAGE_CTX);
    });

    expect(onError).toHaveBeenCalledOnce();
    expect(onError.mock.calls[0][0]).toBeInstanceOf(Error);
  });

  it('passes selected text to sendMessage', async () => {
    mockSendMessage.mockResolvedValue({
      message: makeAssistantMessage(),
      conversation_id: 'c1',
    });

    const { result } = renderHook(() => useChat({ streaming: false }));

    await act(async () => {
      await result.current.send('Explain this', {
        ...PAGE_CTX,
        selectedText: 'some selected passage',
      });
    });

    expect(mockSendMessage).toHaveBeenCalledWith(
      expect.objectContaining({ selected_text: 'some selected passage' })
    );
  });
});

// ---------------------------------------------------------------------------
// newConversation()
// ---------------------------------------------------------------------------

describe('useChat newConversation()', () => {
  it('resets messages to empty', async () => {
    mockSendMessage.mockResolvedValue({
      message: makeAssistantMessage(),
      conversation_id: 'c1',
    });

    const { result } = renderHook(() => useChat({ streaming: false }));

    await act(async () => {
      await result.current.send('Hello', PAGE_CTX);
    });

    expect(result.current.messages.length).toBeGreaterThan(0);

    act(() => {
      result.current.newConversation();
    });

    expect(result.current.messages).toEqual([]);
  });

  it('resets conversationId to null', async () => {
    mockSendMessage.mockResolvedValue({
      message: makeAssistantMessage(),
      conversation_id: 'old-conv',
    });

    const { result } = renderHook(() => useChat({ streaming: false }));

    await act(async () => {
      await result.current.send('Hello', PAGE_CTX);
    });

    expect(result.current.conversationId).toBe('old-conv');

    act(() => {
      result.current.newConversation();
    });

    expect(result.current.conversationId).toBeNull();
  });

  it('resets error state', async () => {
    mockSendMessage.mockRejectedValue(new Error('Oops'));

    const { result } = renderHook(() => useChat({ streaming: false }));

    await act(async () => {
      await result.current.send('Hello', PAGE_CTX);
    });

    expect(result.current.error).toBeTruthy();

    act(() => {
      result.current.newConversation();
    });

    expect(result.current.error).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// clearError()
// ---------------------------------------------------------------------------

describe('useChat clearError()', () => {
  it('clears the error without touching messages', async () => {
    mockSendMessage.mockRejectedValue(new Error('Fail'));

    const { result } = renderHook(() => useChat({ streaming: false }));

    await act(async () => {
      await result.current.send('Hello', PAGE_CTX);
    });

    expect(result.current.error).toBeTruthy();

    act(() => {
      result.current.clearError();
    });

    expect(result.current.error).toBeNull();
    // User message is still in the list
    expect(result.current.messages.length).toBeGreaterThan(0);
  });
});

// ---------------------------------------------------------------------------
// rateFeedback()
// ---------------------------------------------------------------------------

describe('useChat rateFeedback()', () => {
  it('calls submitFeedback with correct args', async () => {
    mockSubmitFeedback.mockResolvedValue(undefined);
    mockSendMessage.mockResolvedValue({
      message: makeAssistantMessage({ id: 'target-msg' }),
      conversation_id: 'c1',
    });

    const { result } = renderHook(() => useChat({ streaming: false }));

    await act(async () => {
      await result.current.send('Hello', PAGE_CTX);
    });

    await act(async () => {
      await result.current.rateFeedback('target-msg', 'up');
    });

    expect(mockSubmitFeedback).toHaveBeenCalledWith('target-msg', 'up');
  });

  it('updates the message feedback in local state', async () => {
    mockSubmitFeedback.mockResolvedValue(undefined);
    const assistantMsg = makeAssistantMessage({ id: 'msg-to-rate' });
    mockSendMessage.mockResolvedValue({
      message: assistantMsg,
      conversation_id: 'c1',
    });

    const { result } = renderHook(() => useChat({ streaming: false }));

    await act(async () => {
      await result.current.send('Hello', PAGE_CTX);
    });

    await act(async () => {
      await result.current.rateFeedback('msg-to-rate', 'down');
    });

    const rated = result.current.messages.find((m) => m.id === 'msg-to-rate');
    expect(rated?.feedback).toBe('down');
  });
});
