"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ChatPanel = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
/**
 * Main chat panel component with input, messages, and context display.
 */
const react_1 = require("react");
const MessageList_1 = require("./MessageList");
const ContextDisplay_1 = require("./ContextDisplay");
const useChat_1 = require("../hooks/useChat");
const useSelection_1 = require("../hooks/useSelection");
const ChatPanel = ({ pageUrl, pageTitle, onClose, }) => {
    const [inputValue, setInputValue] = (0, react_1.useState)('');
    const { selectedText, isTextSelected, clearSelection, } = (0, useSelection_1.useSelection)();
    const { messages, isLoading, isStreaming, error, streamingContent, streamingCitations, send, rateFeedback, newConversation, clearError, } = (0, useChat_1.useChat)({ streaming: true });
    const handleSubmit = (0, react_1.useCallback)(async (e) => {
        e.preventDefault();
        if (!inputValue.trim() || isLoading) {
            return;
        }
        const message = inputValue.trim();
        setInputValue('');
        await send(message, {
            pageUrl,
            pageTitle,
            selectedText: isTextSelected ? selectedText : undefined,
        });
    }, [inputValue, isLoading, send, pageUrl, pageTitle, isTextSelected, selectedText]);
    const handleKeyDown = (0, react_1.useCallback)((e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    }, [handleSubmit]);
    return ((0, jsx_runtime_1.jsxs)("div", { className: "rag-chat-panel", children: [(0, jsx_runtime_1.jsxs)("div", { className: "rag-chat-header", children: [(0, jsx_runtime_1.jsx)("h3", { className: "rag-chat-title", children: "Documentation Assistant" }), (0, jsx_runtime_1.jsxs)("div", { className: "rag-chat-actions", children: [(0, jsx_runtime_1.jsx)("button", { className: "rag-btn rag-btn-secondary", onClick: newConversation, title: "Start new conversation", children: "New Chat" }), onClose && ((0, jsx_runtime_1.jsx)("button", { className: "rag-btn rag-btn-icon", onClick: onClose, "aria-label": "Close chat", children: "\u00D7" }))] })] }), isTextSelected && ((0, jsx_runtime_1.jsx)(ContextDisplay_1.ContextDisplay, { selectedText: selectedText, onClear: clearSelection })), (0, jsx_runtime_1.jsx)(MessageList_1.MessageList, { messages: messages, isStreaming: isStreaming, streamingContent: streamingContent, streamingCitations: streamingCitations, onFeedback: rateFeedback }), error && ((0, jsx_runtime_1.jsxs)("div", { className: "rag-error", children: [(0, jsx_runtime_1.jsx)("span", { children: error }), (0, jsx_runtime_1.jsx)("button", { onClick: clearError, "aria-label": "Dismiss error", children: "\u00D7" })] })), (0, jsx_runtime_1.jsxs)("form", { className: "rag-chat-input-form", onSubmit: handleSubmit, children: [(0, jsx_runtime_1.jsx)("textarea", { className: "rag-chat-input", value: inputValue, onChange: (e) => setInputValue(e.target.value), onKeyDown: handleKeyDown, placeholder: isTextSelected
                            ? 'Ask about the selected text...'
                            : 'Select text and ask a question...', rows: 2, disabled: isLoading }), (0, jsx_runtime_1.jsx)("button", { type: "submit", className: "rag-btn rag-btn-primary", disabled: !inputValue.trim() || isLoading, children: isLoading ? 'Sending...' : 'Send' })] })] }));
};
exports.ChatPanel = ChatPanel;
exports.default = exports.ChatPanel;
//# sourceMappingURL=ChatPanel.js.map