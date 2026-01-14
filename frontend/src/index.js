"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.useSelection = exports.useChat = exports.ChatPanel = exports.ChatWidget = void 0;
exports.initWidget = initWidget;
const jsx_runtime_1 = require("react/jsx-runtime");
/**
 * Widget entry point with Shadow DOM mounting.
 *
 * Creates an isolated widget that can be embedded in any page.
 */
const react_1 = __importDefault(require("react"));
const client_1 = require("react-dom/client");
const ChatWidget_1 = require("./components/ChatWidget");
// Default configuration
const DEFAULT_CONFIG = {
    position: 'bottom-right',
    defaultOpen: false,
};
/**
 * Initialize the RAG chatbot widget.
 *
 * @param containerId - ID of the container element (optional, creates one if not provided)
 * @param config - Widget configuration
 */
function initWidget(containerId, config = {}) {
    const mergedConfig = { ...DEFAULT_CONFIG, ...config };
    // Set API URL if provided
    if (mergedConfig.apiUrl) {
        window.__RAG_API_URL__ = mergedConfig.apiUrl;
    }
    // Find or create container
    let container = containerId ? document.getElementById(containerId) : null;
    if (!container) {
        container = document.createElement('div');
        container.id = 'rag-chatbot-widget';
        document.body.appendChild(container);
    }
    // Create Shadow DOM for style isolation
    const shadowRoot = container.attachShadow({ mode: 'open' });
    // Create style element with widget styles
    const styleElement = document.createElement('style');
    styleElement.textContent = getWidgetStyles();
    shadowRoot.appendChild(styleElement);
    // Create mount point inside shadow DOM
    const mountPoint = document.createElement('div');
    mountPoint.className = 'rag-widget-root';
    shadowRoot.appendChild(mountPoint);
    // Render React app
    const root = (0, client_1.createRoot)(mountPoint);
    root.render((0, jsx_runtime_1.jsx)(react_1.default.StrictMode, { children: (0, jsx_runtime_1.jsx)(ChatWidget_1.ChatWidget, { position: mergedConfig.position, defaultOpen: mergedConfig.defaultOpen }) }));
}
/**
 * Get widget styles as a string for Shadow DOM injection.
 */
function getWidgetStyles() {
    // Import styles at build time
    return `
    /* Widget styles - will be replaced by build process */
    @import url('./styles/widget.css');
  `;
}
// Auto-initialize if script tag has data-auto-init
if (document.currentScript?.hasAttribute('data-auto-init')) {
    document.addEventListener('DOMContentLoaded', () => {
        const script = document.currentScript;
        const config = {
            position: script.dataset.position || 'bottom-right',
            defaultOpen: script.dataset.defaultOpen === 'true',
            apiUrl: script.dataset.apiUrl,
        };
        initWidget(undefined, config);
    });
}
// Export for manual initialization
var ChatWidget_2 = require("./components/ChatWidget");
Object.defineProperty(exports, "ChatWidget", { enumerable: true, get: function () { return ChatWidget_2.ChatWidget; } });
var ChatPanel_1 = require("./components/ChatPanel");
Object.defineProperty(exports, "ChatPanel", { enumerable: true, get: function () { return ChatPanel_1.ChatPanel; } });
var useChat_1 = require("./hooks/useChat");
Object.defineProperty(exports, "useChat", { enumerable: true, get: function () { return useChat_1.useChat; } });
var useSelection_1 = require("./hooks/useSelection");
Object.defineProperty(exports, "useSelection", { enumerable: true, get: function () { return useSelection_1.useSelection; } });
//# sourceMappingURL=index.js.map