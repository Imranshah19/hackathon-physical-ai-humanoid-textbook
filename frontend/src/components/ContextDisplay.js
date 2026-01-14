"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ContextDisplay = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
const useTranslation_1 = require("../hooks/useTranslation");
const ContextDisplay = ({ selectedText, onClear, }) => {
    const { translatedText, isTranslating, error, translateToUrdu, clearTranslation, isShowingTranslation, toggleTranslation, } = (0, useTranslation_1.useTranslation)();
    if (!selectedText) {
        return null;
    }
    const displayText = isShowingTranslation && translatedText ? translatedText : selectedText;
    const truncatedText = displayText.length > 300
        ? displayText.slice(0, 300) + '...'
        : displayText;
    const handleTranslate = () => {
        if (translatedText) {
            toggleTranslation();
        }
        else {
            translateToUrdu(selectedText);
        }
    };
    const handleClear = () => {
        clearTranslation();
        onClear();
    };
    return ((0, jsx_runtime_1.jsxs)("div", { className: "rag-context-display", children: [(0, jsx_runtime_1.jsxs)("div", { className: "rag-context-header", children: [(0, jsx_runtime_1.jsx)("span", { className: "rag-context-label", children: isShowingTranslation ? 'اردو ترجمہ' : 'Selected Context' }), (0, jsx_runtime_1.jsxs)("div", { className: "rag-context-actions", children: [(0, jsx_runtime_1.jsx)("button", { className: `rag-context-translate ${isShowingTranslation ? 'rag-context-translate-active' : ''}`, onClick: handleTranslate, disabled: isTranslating, "aria-label": isShowingTranslation ? 'Show original' : 'Translate to Urdu', title: isShowingTranslation ? 'Show original' : 'Translate to Urdu (اردو)', children: isTranslating ? ((0, jsx_runtime_1.jsx)("span", { className: "rag-translate-spinner", children: "\u27F3" })) : ((0, jsx_runtime_1.jsxs)(jsx_runtime_1.Fragment, { children: [(0, jsx_runtime_1.jsx)("span", { className: "rag-translate-icon", children: "\uD83C\uDF10" }), (0, jsx_runtime_1.jsx)("span", { className: "rag-translate-label", children: isShowingTranslation ? 'Original' : 'اردو' })] })) }), (0, jsx_runtime_1.jsx)("button", { className: "rag-context-clear", onClick: handleClear, "aria-label": "Clear selection", children: "\u00D7" })] })] }), error && (0, jsx_runtime_1.jsx)("div", { className: "rag-context-error", children: error }), (0, jsx_runtime_1.jsx)("div", { className: `rag-context-text ${isShowingTranslation ? 'rag-context-text-urdu' : ''}`, dir: isShowingTranslation ? 'rtl' : 'ltr', lang: isShowingTranslation ? 'ur' : 'en', children: truncatedText })] }));
};
exports.ContextDisplay = ContextDisplay;
exports.default = exports.ContextDisplay;
//# sourceMappingURL=ContextDisplay.js.map