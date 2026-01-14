/**
 * Component to render the list of chat messages.
 */
import React from 'react';
import type { Message, Citation } from '../services/api';
interface MessageListProps {
    messages: Message[];
    isStreaming: boolean;
    streamingContent: string;
    streamingCitations: Citation[];
    onFeedback?: (messageId: string, feedback: 'up' | 'down') => void;
}
export declare const MessageList: React.FC<MessageListProps>;
export default MessageList;
//# sourceMappingURL=MessageList.d.ts.map