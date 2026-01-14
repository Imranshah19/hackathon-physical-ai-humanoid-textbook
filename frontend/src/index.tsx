/**
 * Widget entry point with Shadow DOM mounting.
 *
 * Creates an isolated widget that can be embedded in any page.
 */

import React from 'react';
import { createRoot } from 'react-dom/client';
import { ChatWidget } from './components/ChatWidget';

// Widget configuration interface
interface WidgetConfig {
  position?: 'bottom-right' | 'bottom-left';
  defaultOpen?: boolean;
  apiUrl?: string;
}

// Default configuration
const DEFAULT_CONFIG: WidgetConfig = {
  position: 'bottom-right',
  defaultOpen: false,
};

/**
 * Initialize the RAG chatbot widget.
 *
 * @param containerId - ID of the container element (optional, creates one if not provided)
 * @param config - Widget configuration
 */
export function initWidget(
  containerId?: string,
  config: WidgetConfig = {}
): void {
  const mergedConfig = { ...DEFAULT_CONFIG, ...config };

  // Set API URL if provided
  if (mergedConfig.apiUrl) {
    (window as any).__RAG_API_URL__ = mergedConfig.apiUrl;
  }

  // Find or create container
  let container = containerId ? document.getElementById(containerId) : null;

  if (!container) {
    container = document.createElement('div');
    container.id = 'rag-chatbot-widget';
    document.body.appendChild(container);
  }

  // Create Shadow DOM for style isolation
  const shadowRoot = container.attachShadow({ mode: 'open' });

  // Create style element with widget styles
  const styleElement = document.createElement('style');
  styleElement.textContent = getWidgetStyles();
  shadowRoot.appendChild(styleElement);

  // Create mount point inside shadow DOM
  const mountPoint = document.createElement('div');
  mountPoint.className = 'rag-widget-root';
  shadowRoot.appendChild(mountPoint);

  // Render React app
  const root = createRoot(mountPoint);
  root.render(
    <React.StrictMode>
      <ChatWidget
        position={mergedConfig.position}
        defaultOpen={mergedConfig.defaultOpen}
      />
    </React.StrictMode>
  );
}

/**
 * Get widget styles as a string for Shadow DOM injection.
 */
function getWidgetStyles(): string {
  // Import styles at build time
  return `
    /* Widget styles - will be replaced by build process */
    @import url('./styles/widget.css');
  `;
}

// Auto-initialize if script tag has data-auto-init
if (document.currentScript?.hasAttribute('data-auto-init')) {
  document.addEventListener('DOMContentLoaded', () => {
    const script = document.currentScript as HTMLScriptElement;
    const config: WidgetConfig = {
      position: (script.dataset.position as WidgetConfig['position']) || 'bottom-right',
      defaultOpen: script.dataset.defaultOpen === 'true',
      apiUrl: script.dataset.apiUrl,
    };
    initWidget(undefined, config);
  });
}

// Export for manual initialization
export { ChatWidget } from './components/ChatWidget';
export { ChatPanel } from './components/ChatPanel';
export { useChat } from './hooks/useChat';
export { useSelection } from './hooks/useSelection';
