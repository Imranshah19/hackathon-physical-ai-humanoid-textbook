/**
 * Widget entry point with Shadow DOM mounting.
 *
 * Creates an isolated widget that can be embedded in any page.
 */
interface WidgetConfig {
    position?: 'bottom-right' | 'bottom-left';
    defaultOpen?: boolean;
    apiUrl?: string;
}
/**
 * Initialize the RAG chatbot widget.
 *
 * @param containerId - ID of the container element (optional, creates one if not provided)
 * @param config - Widget configuration
 */
export declare function initWidget(containerId?: string, config?: WidgetConfig): void;
export { ChatWidget } from './components/ChatWidget';
export { ChatPanel } from './components/ChatPanel';
export { useChat } from './hooks/useChat';
export { useSelection } from './hooks/useSelection';
//# sourceMappingURL=index.d.ts.map