/**
 * Code example viewer with language tabs (T045).
 *
 * Displays code examples with syntax highlighting and language switching.
 */

import React, { useState, useCallback, useMemo } from 'react';

interface CodeExampleViewerProps {
  /** Example identifier */
  exampleId: string;
  /** Example title */
  title: string;
  /** Example description */
  description?: string;
  /** Code in different languages: { python: "...", cpp: "..." } */
  languages: Record<string, string>;
  /** Initially selected language */
  preferredLanguage?: string;
  /** Expected output (optional) */
  output?: string;
  /** Callback when language is switched */
  onLanguageChange?: (language: string) => void;
  /** Show copy button */
  showCopy?: boolean;
  /** Show line numbers */
  showLineNumbers?: boolean;
}

const LANGUAGE_LABELS: Record<string, string> = {
  python: 'Python',
  cpp: 'C++',
  javascript: 'JavaScript',
  typescript: 'TypeScript',
  bash: 'Bash',
  yaml: 'YAML',
  json: 'JSON',
};

export const CodeExampleViewer: React.FC<CodeExampleViewerProps> = ({
  exampleId,
  title,
  description,
  languages,
  preferredLanguage,
  output,
  onLanguageChange,
  showCopy = true,
  showLineNumbers = true,
}) => {
  // Available languages
  const availableLanguages = useMemo(() => Object.keys(languages), [languages]);

  // Current language
  const [currentLanguage, setCurrentLanguage] = useState(() => {
    if (preferredLanguage && languages[preferredLanguage]) {
      return preferredLanguage;
    }
    return availableLanguages[0] || 'python';
  });

  // Copy state
  const [copied, setCopied] = useState(false);

  // Handle language switch
  const handleLanguageSwitch = useCallback(
    (lang: string) => {
      setCurrentLanguage(lang);
      onLanguageChange?.(lang);
    },
    [onLanguageChange]
  );

  // Handle copy
  const handleCopy = useCallback(async () => {
    const code = languages[currentLanguage];
    if (!code) return;

    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  }, [languages, currentLanguage]);

  // Get current code
  const currentCode = languages[currentLanguage] || '';

  // Add line numbers
  const codeWithLineNumbers = useMemo(() => {
    if (!showLineNumbers) return currentCode;
    const lines = currentCode.split('\n');
    const padding = String(lines.length).length;
    return lines
      .map((line, i) => {
        const lineNum = String(i + 1).padStart(padding, ' ');
        return `${lineNum} │ ${line}`;
      })
      .join('\n');
  }, [currentCode, showLineNumbers]);

  return (
    <div className="code-example" id={`code-${exampleId}`}>
      {/* Header */}
      <div className="code-example-header">
        <div className="code-example-info">
          <h4 className="code-example-title">{title}</h4>
          {description && <p className="code-example-description">{description}</p>}
        </div>

        {/* Language tabs */}
        {availableLanguages.length > 1 && (
          <div className="code-example-tabs" role="tablist">
            {availableLanguages.map((lang) => (
              <button
                key={lang}
                role="tab"
                aria-selected={currentLanguage === lang}
                className={`code-example-tab ${
                  currentLanguage === lang ? 'code-example-tab-active' : ''
                }`}
                onClick={() => handleLanguageSwitch(lang)}
              >
                {LANGUAGE_LABELS[lang] || lang}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Code block */}
      <div className="code-example-content">
        <pre className={`code-example-pre language-${currentLanguage}`}>
          <code>{showLineNumbers ? codeWithLineNumbers : currentCode}</code>
        </pre>

        {/* Copy button */}
        {showCopy && (
          <button
            className={`code-example-copy ${copied ? 'code-example-copy-success' : ''}`}
            onClick={handleCopy}
            aria-label={copied ? 'Copied!' : 'Copy code'}
          >
            {copied ? '✓ Copied' : 'Copy'}
          </button>
        )}
      </div>

      {/* Output */}
      {output && (
        <div className="code-example-output">
          <span className="code-example-output-label">Output:</span>
          <pre className="code-example-output-content">{output}</pre>
        </div>
      )}
    </div>
  );
};

export default CodeExampleViewer;
