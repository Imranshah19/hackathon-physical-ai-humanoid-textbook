/**
 * Component to render a clickable citation link.
 */
import React from 'react';
import type { Citation } from '../services/api';
interface CitationLinkProps {
    citation: Citation;
    index: number;
}
export declare const CitationLink: React.FC<CitationLinkProps>;
interface CitationListProps {
    citations: Citation[];
}
export declare const CitationList: React.FC<CitationListProps>;
export default CitationLink;
//# sourceMappingURL=CitationLink.d.ts.map