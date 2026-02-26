"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = ChatWidgetWrapper;
const jsx_runtime_1 = require("react/jsx-runtime");
/**
 * Docusaurus theme wrapper for the chat widget.
 *
 * Provides React component integration with Docusaurus theme system.
 */
const react_1 = require("react");
const router_1 = require("@docusaurus/router");
const useGlobalData_1 = require("@docusaurus/useGlobalData");
/**
 * Wrapper component that conditionally renders the chat widget
 * based on plugin configuration and current route.
 */
function ChatWidgetWrapper({ children, }) {
    const location = (0, router_1.useLocation)();
    const [Widget, setWidget] = (0, react_1.useState)(null);
    // Get plugin configuration
    const pluginData = (0, useGlobalData_1.usePluginData)('docusaurus-plugin-rag-chatbot');
    const config = pluginData?.config || {
        apiUrl: 'http://localhost:8000/api/v1',
        position: 'bottom-right',
        defaultOpen: false,
        excludePages: [],
    };
    // Check if current page is excluded
    const isExcluded = config.excludePages.some((pattern) => {
        const regex = new RegExp(pattern);
        return regex.test(location.pathname);
    });
    // Dynamically load widget component
    (0, react_1.useEffect)(() => {
        if (isExcluded) {
            return;
        }
        Promise.resolve().then(() => __importStar(require('@rag-chatbot/widget'))).then((module) => {
            setWidget(() => module.ChatWidget);
        })
            .catch((error) => {
            console.error('Failed to load chat widget:', error);
        });
    }, [isExcluded]);
    return ((0, jsx_runtime_1.jsxs)(jsx_runtime_1.Fragment, { children: [children, !isExcluded && Widget && ((0, jsx_runtime_1.jsx)(Widget, { position: config.position, defaultOpen: config.defaultOpen }))] }));
}
//# sourceMappingURL=ChatWidgetWrapper.js.map