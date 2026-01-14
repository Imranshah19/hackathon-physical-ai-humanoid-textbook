/**
 * Docusaurus Plugin for RAG Documentation Chatbot
 *
 * Integrates the chat widget into Docusaurus documentation sites.
 */
import type { LoadContext, Plugin } from '@docusaurus/types';
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
export default function pluginRagChatbot(context: LoadContext, options: PluginOptions): Plugin;
export { validateOptions } from './options';
//# sourceMappingURL=index.d.ts.map