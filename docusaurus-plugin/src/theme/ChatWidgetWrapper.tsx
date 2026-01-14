/**
 * Docusaurus theme wrapper for the chat widget.
 *
 * Provides React component integration with Docusaurus theme system.
 */

import React, { useEffect, useState } from 'react';
import { useLocation } from '@docusaurus/router';
import { usePluginData } from '@docusaurus/useGlobalData';

interface ChatWidgetWrapperProps {
  children?: React.ReactNode;
}

interface PluginConfig {
  apiUrl: string;
  position: 'bottom-right' | 'bottom-left';
  defaultOpen: boolean;
  excludePages: string[];
}

/**
 * Wrapper component that conditionally renders the chat widget
 * based on plugin configuration and current route.
 */
export default function ChatWidgetWrapper({
  children,
}: ChatWidgetWrapperProps): JSX.Element {
  const location = useLocation();
  const [Widget, setWidget] = useState<React.ComponentType<any> | null>(null);

  // Get plugin configuration
  const pluginData = usePluginData('docusaurus-plugin-rag-chatbot') as {
    config: PluginConfig;
  } | undefined;

  const config = pluginData?.config || {
    apiUrl: 'http://localhost:8000/api/v1',
    position: 'bottom-right' as const,
    defaultOpen: false,
    excludePages: [],
  };

  // Check if current page is excluded
  const isExcluded = config.excludePages.some((pattern) => {
    const regex = new RegExp(pattern);
    return regex.test(location.pathname);
  });

  // Dynamically load widget component
  useEffect(() => {
    if (isExcluded) {
      return;
    }

    import('@rag-chatbot/widget')
      .then((module) => {
        setWidget(() => module.ChatWidget);
      })
      .catch((error) => {
        console.error('Failed to load chat widget:', error);
      });
  }, [isExcluded]);

  return (
    <>
      {children}
      {!isExcluded && Widget && (
        <Widget
          position={config.position}
          defaultOpen={config.defaultOpen}
        />
      )}
    </>
  );
}
