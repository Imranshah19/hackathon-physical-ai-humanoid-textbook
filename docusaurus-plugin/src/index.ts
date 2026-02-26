/**
 * Docusaurus Plugin for RAG Documentation Chatbot
 *
 * Integrates the chat widget into Docusaurus documentation sites.
 */

import type { LoadContext, Plugin } from '@docusaurus/types';
import path from 'path';

export interface PluginOptions {
  /** API URL for the chatbot backend */
  apiUrl?: string;
  /** Widget position */
  position?: 'bottom-right' | 'bottom-left';
  /** Whether to open widget by default */
  defaultOpen?: boolean;
  /** Pages to exclude (regex patterns) */
  excludePages?: string[];
}

const DEFAULT_OPTIONS: Required<PluginOptions> = {
  apiUrl: 'http://localhost:8000/api/v1',
  position: 'bottom-right',
  defaultOpen: false,
  excludePages: [],
};

export default function pluginRagChatbot(
  context: LoadContext,
  options: PluginOptions
): Plugin {
  const mergedOptions = { ...DEFAULT_OPTIONS, ...options };

  return {
    name: 'docusaurus-plugin-rag-chatbot',

    getThemePath() {
      return path.resolve(__dirname, './theme');
    },

    getClientModules() {
      return [path.resolve(__dirname, './client-module')];
    },

    configureWebpack() {
      return {
        resolve: {
          alias: {
            '@rag-chatbot/widget': path.resolve(__dirname, '../../frontend/src'),
          },
        },
      };
    },

    injectHtmlTags() {
      return {
        headTags: [
          {
            tagName: 'script',
            attributes: {
              type: 'text/javascript',
            },
            innerHTML: `
              window.__RAG_CHATBOT_CONFIG__ = ${JSON.stringify(mergedOptions)};
            `,
          },
        ],
      };
    },

    async contentLoaded({ actions }) {
      const { setGlobalData } = actions;
      setGlobalData({
        config: mergedOptions,
      });
    },
  };
}

export { validateOptions } from './options';
