/**
 * Vitest global test setup.
 *
 * Runs before every test file.
 */
import { vi, beforeEach, afterEach } from 'vitest';

// Polyfill crypto.randomUUID for jsdom
if (!globalThis.crypto?.randomUUID) {
  let counter = 0;
  Object.defineProperty(globalThis, 'crypto', {
    value: {
      randomUUID: () => `test-uuid-${String(++counter).padStart(4, '0')}-0000-0000-0000-000000000000`,
      getRandomValues: (arr: Uint8Array) => {
        for (let i = 0; i < arr.length; i++) arr[i] = Math.floor(Math.random() * 256);
        return arr;
      },
    },
    writable: true,
  });
}

// Clear localStorage between tests to avoid state leakage
beforeEach(() => {
  localStorage.clear();
});

afterEach(() => {
  vi.restoreAllMocks();
});
