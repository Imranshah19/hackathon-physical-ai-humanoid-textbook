"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.MessageList = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
/**
 * Component to render the list of chat messages.
 */
const react_1 = __importDefault(require("react"));
const CitationLink_1 = require("./CitationLink");
const MessageItem = ({ message, onFeedback }) => {
    const isUser = message.role === 'user';
    return ((0, jsx_runtime_1.jsxs)("div", { className: `rag-message ${isUser ? 'rag-message-user' : 'rag-message-assistant'}`, children: [(0, jsx_runtime_1.jsx)("div", { className: "rag-message-content", children: message.content }), !isUser && message.citations.length > 0 && ((0, jsx_runtime_1.jsx)(CitationLink_1.CitationList, { citations: message.citations })), !isUser && onFeedback && ((0, jsx_runtime_1.jsxs)("div", { className: "rag-message-feedback", children: [(0, jsx_runtime_1.jsx)("button", { className: `rag-feedback-btn ${message.feedback === 'up' ? 'active' : ''}`, onClick: () => onFeedback(message.id, 'up'), "aria-label": "Helpful", children: "\uD83D\uDC4D" }), (0, jsx_runtime_1.jsx)("button", { className: `rag-feedback-btn ${message.feedback === 'down' ? 'active' : ''}`, onClick: () => onFeedback(message.id, 'down'), "aria-label": "Not helpful", children: "\uD83D\uDC4E" })] }))] }));
};
const StreamingMessage = ({ content, citations, }) => {
    return ((0, jsx_runtime_1.jsxs)("div", { className: "rag-message rag-message-assistant rag-message-streaming", children: [(0, jsx_runtime_1.jsxs)("div", { className: "rag-message-content", children: [content, (0, jsx_runtime_1.jsx)("span", { className: "rag-typing-indicator", children: "\u258A" })] }), citations.length > 0 && (0, jsx_runtime_1.jsx)(CitationLink_1.CitationList, { citations: citations })] }));
};
const MessageList = ({ messages, isStreaming, streamingContent, streamingCitations, onFeedback, }) => {
    const messagesEndRef = react_1.default.useRef(null);
    // Auto-scroll to bottom on new messages
    react_1.default.useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, streamingContent]);
    if (messages.length === 0 && !isStreaming) {
        return ((0, jsx_runtime_1.jsx)("div", { className: "rag-messages-empty", children: (0, jsx_runtime_1.jsx)("p", { children: "Select text from the documentation and ask a question about it." }) }));
    }
    return ((0, jsx_runtime_1.jsxs)("div", { className: "rag-messages", children: [messages.map((message) => ((0, jsx_runtime_1.jsx)(MessageItem, { message: message, onFeedback: onFeedback }, message.id))), isStreaming && ((0, jsx_runtime_1.jsx)(StreamingMessage, { content: streamingContent, citations: streamingCitations })), (0, jsx_runtime_1.jsx)("div", { ref: messagesEndRef })] }));
};
exports.MessageList = MessageList;
exports.default = exports.MessageList;
//# sourceMappingURL=MessageList.js.map