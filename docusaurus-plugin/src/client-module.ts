/**
 * Client-side module for initializing the chat widget.
 */

import ExecutionEnvironment from '@docusaurus/ExecutionEnvironment';

if (ExecutionEnvironment.canUseDOM) {
  // Initialize widget when DOM is ready
  const initWidget = () => {
    const config = (window as any).__RAG_CHATBOT_CONFIG__ || {};

    // Check if current page is excluded
    const currentPath = window.location.pathname;
    const excludePages: string[] = config.excludePages || [];

    const isExcluded = excludePages.some((pattern) => {
      const regex = new RegExp(pattern);
      return regex.test(currentPath);
    });

    if (isExcluded) {
      return;
    }

    // Dynamically import and initialize widget
    import('@rag-chatbot/widget').then(({ initWidget }) => {
      initWidget(undefined, {
        position: config.position,
        defaultOpen: config.defaultOpen,
        apiUrl: config.apiUrl,
      });
    }).catch((error) => {
      console.error('Failed to load RAG chatbot widget:', error);
    });
  };

  // Initialize on DOM content loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initWidget);
  } else {
    initWidget();
  }
}

export default {};
