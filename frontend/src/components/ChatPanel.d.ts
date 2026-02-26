/**
 * Main chat panel component with input, messages, and context display.
 */
import React from 'react';
interface ChatPanelProps {
    /** Current page URL for context */
    pageUrl: string;
    /** Current page title */
    pageTitle?: string;
    /** Callback when panel is closed */
    onClose?: () => void;
}
export declare const ChatPanel: React.FC<ChatPanelProps>;
export default ChatPanel;
//# sourceMappingURL=ChatPanel.d.ts.map