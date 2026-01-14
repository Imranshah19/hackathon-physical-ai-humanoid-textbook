"use strict";
/**
 * Client-side module for initializing the chat widget.
 */
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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const ExecutionEnvironment_1 = __importDefault(require("@docusaurus/ExecutionEnvironment"));
if (ExecutionEnvironment_1.default.canUseDOM) {
    // Initialize widget when DOM is ready
    const initWidget = () => {
        const config = window.__RAG_CHATBOT_CONFIG__ || {};
        // Check if current page is excluded
        const currentPath = window.location.pathname;
        const excludePages = config.excludePages || [];
        const isExcluded = excludePages.some((pattern) => {
            const regex = new RegExp(pattern);
            return regex.test(currentPath);
        });
        if (isExcluded) {
            return;
        }
        // Dynamically import and initialize widget
        Promise.resolve().then(() => __importStar(require('@rag-chatbot/widget'))).then(({ initWidget }) => {
            initWidget(undefined, {
                position: config.position,
                defaultOpen: config.defaultOpen,
                apiUrl: config.apiUrl,
            });
        }).catch((error) => {
            console.error('Failed to load RAG chatbot widget:', error);
        });
    };
    // Initialize on DOM content loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initWidget);
    }
    else {
        initWidget();
    }
}
exports.default = {};
//# sourceMappingURL=client-module.js.map