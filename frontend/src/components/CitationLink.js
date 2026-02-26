"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CitationList = exports.CitationLink = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
const CitationLink = ({ citation, index, }) => {
    const handleClick = () => {
        if (citation.source_url) {
            // Navigate to source
            window.location.href = citation.source_url;
        }
    };
    return ((0, jsx_runtime_1.jsxs)("button", { className: "rag-citation-link", onClick: handleClick, title: citation.text, "aria-label": `Citation ${index + 1}: ${citation.section_title || citation.source_url}`, children: [(0, jsx_runtime_1.jsxs)("span", { className: "rag-citation-number", children: ["[", index + 1, "]"] }), citation.section_title && ((0, jsx_runtime_1.jsx)("span", { className: "rag-citation-title", children: citation.section_title }))] }));
};
exports.CitationLink = CitationLink;
const CitationList = ({ citations }) => {
    if (!citations.length) {
        return null;
    }
    return ((0, jsx_runtime_1.jsxs)("div", { className: "rag-citations", children: [(0, jsx_runtime_1.jsx)("span", { className: "rag-citations-label", children: "Sources:" }), (0, jsx_runtime_1.jsx)("div", { className: "rag-citations-list", children: citations.map((citation, index) => ((0, jsx_runtime_1.jsx)(exports.CitationLink, { citation: citation, index: index }, index))) })] }));
};
exports.CitationList = CitationList;
exports.default = exports.CitationLink;
//# sourceMappingURL=CitationLink.js.map