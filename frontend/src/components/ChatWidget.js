"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ChatWidget = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
/**
 * Floating chat widget component with toggle button and panel.
 */
const react_1 = require("react");
const ChatPanel_1 = require("./ChatPanel");
const ChatWidget = ({ position = 'bottom-right', defaultOpen = false, }) => {
    const [isOpen, setIsOpen] = (0, react_1.useState)(defaultOpen);
    const toggleOpen = (0, react_1.useCallback)(() => {
        setIsOpen((prev) => !prev);
    }, []);
    const handleClose = (0, react_1.useCallback)(() => {
        setIsOpen(false);
    }, []);
    // Get current page info
    const pageUrl = window.location.pathname;
    const pageTitle = document.title;
    return ((0, jsx_runtime_1.jsxs)("div", { className: `rag-widget rag-widget-${position}`, children: [isOpen && ((0, jsx_runtime_1.jsx)(ChatPanel_1.ChatPanel, { pageUrl: pageUrl, pageTitle: pageTitle, onClose: handleClose })), (0, jsx_runtime_1.jsx)("button", { className: `rag-widget-toggle ${isOpen ? 'rag-widget-toggle-open' : ''}`, onClick: toggleOpen, "aria-label": isOpen ? 'Close chat' : 'Open chat', "aria-expanded": isOpen, children: isOpen ? ((0, jsx_runtime_1.jsx)(CloseIcon, {})) : ((0, jsx_runtime_1.jsx)(ChatIcon, {})) })] }));
};
exports.ChatWidget = ChatWidget;
const ChatIcon = () => ((0, jsx_runtime_1.jsx)("svg", { width: "24", height: "24", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", children: (0, jsx_runtime_1.jsx)("path", { d: "M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" }) }));
const CloseIcon = () => ((0, jsx_runtime_1.jsxs)("svg", { width: "24", height: "24", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", children: [(0, jsx_runtime_1.jsx)("line", { x1: "18", y1: "6", x2: "6", y2: "18" }), (0, jsx_runtime_1.jsx)("line", { x1: "6", y1: "6", x2: "18", y2: "18" })] }));
exports.default = exports.ChatWidget;
//# sourceMappingURL=ChatWidget.js.map