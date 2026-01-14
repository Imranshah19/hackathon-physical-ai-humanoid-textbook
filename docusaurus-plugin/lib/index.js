"use strict";
/**
 * Docusaurus Plugin for RAG Documentation Chatbot
 *
 * Integrates the chat widget into Docusaurus documentation sites.
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.validateOptions = void 0;
exports.default = pluginRagChatbot;
const path_1 = __importDefault(require("path"));
const DEFAULT_OPTIONS = {
    apiUrl: 'http://localhost:8000/api/v1',
    position: 'bottom-right',
    defaultOpen: false,
    excludePages: [],
};
function pluginRagChatbot(context, options) {
    const mergedOptions = { ...DEFAULT_OPTIONS, ...options };
    return {
        name: 'docusaurus-plugin-rag-chatbot',
        getThemePath() {
            return path_1.default.resolve(__dirname, './theme');
        },
        getClientModules() {
            return [path_1.default.resolve(__dirname, './client-module')];
        },
        configureWebpack() {
            return {
                resolve: {
                    alias: {
                        '@rag-chatbot/widget': path_1.default.resolve(__dirname, '../../frontend/src'),
                    },
                },
            };
        },
        injectHtmlTags() {
            return {
                headTags: [
                    {
                        tagName: 'script',
                        attributes: {
                            type: 'text/javascript',
                        },
                        innerHTML: `
              window.__RAG_CHATBOT_CONFIG__ = ${JSON.stringify(mergedOptions)};
            `,
                    },
                ],
            };
        },
        async contentLoaded({ actions }) {
            const { setGlobalData } = actions;
            setGlobalData({
                config: mergedOptions,
            });
        },
    };
}
var options_1 = require("./options");
Object.defineProperty(exports, "validateOptions", { enumerable: true, get: function () { return options_1.validateOptions; } });
//# sourceMappingURL=index.js.map