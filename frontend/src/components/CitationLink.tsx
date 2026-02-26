/**
 * Component to render a clickable citation link.
 */

import React from 'react';
import type { Citation } from '../services/api';

interface CitationLinkProps {
  citation: Citation;
  index: number;
}

export const CitationLink: React.FC<CitationLinkProps> = ({
  citation,
  index,
}) => {
  const handleClick = () => {
    if (citation.source_url) {
      // Navigate to source
      window.location.href = citation.source_url;
    }
  };

  return (
    <button
      className="rag-citation-link"
      onClick={handleClick}
      title={citation.text}
      aria-label={`Citation ${index + 1}: ${citation.section_title || citation.source_url}`}
    >
      <span className="rag-citation-number">[{index + 1}]</span>
      {citation.section_title && (
        <span className="rag-citation-title">{citation.section_title}</span>
      )}
    </button>
  );
};

interface CitationListProps {
  citations: Citation[];
}

export const CitationList: React.FC<CitationListProps> = ({ citations }) => {
  if (!citations.length) {
    return null;
  }

  return (
    <div className="rag-citations">
      <span className="rag-citations-label">Sources:</span>
      <div className="rag-citations-list">
        {citations.map((citation, index) => (
          <CitationLink key={index} citation={citation} index={index} />
        ))}
      </div>
    </div>
  );
};

export default CitationLink;
