/* ArtifactViewer — renders Markdown or HTML artifacts with actions */

import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { X, FileText, Code, Copy, Check, Download, RefreshCw, ChevronsLeft, ChevronsRight } from 'lucide-react';
import type { Artifact, Message } from '../types';

interface ArtifactViewerProps {
  messagesWithArtifacts: Message[];
  activeArtifact: Artifact | null;
  onSelectArtifact: (artifact: Artifact) => void;
  onClose: () => void;
  onRegenerate?: () => void;
  isLoading?: boolean;
}

export function ArtifactViewer({
  messagesWithArtifacts,
  activeArtifact,
  onSelectArtifact,
  onClose,
  onRegenerate,
  isLoading,
}: ArtifactViewerProps) {
  const [copied, setCopied] = useState(false);
  const [showSidebar, setShowSidebar] = useState(() => {
    const saved = localStorage.getItem('lenny_showArtifactSidebar');
    return saved !== null ? saved === 'true' : true;
  });

  useEffect(() => {
    localStorage.setItem('lenny_showArtifactSidebar', showSidebar.toString());
  }, [showSidebar]);

  // --- Action handlers ---
  const handleCopy = () => {
    if (!activeArtifact) return;
    navigator.clipboard.writeText(activeArtifact.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!activeArtifact) return;
    const ext = activeArtifact.type === 'html' ? 'html' : 'md';
    const mimeType = activeArtifact.type === 'html' ? 'text/html' : 'text/markdown';
    const filename = `${(activeArtifact.title || 'document').replace(/[^a-zA-Z0-9\s-]/g, '').replace(/\s+/g, '_')}.${ext}`;
    const blob = new Blob([activeArtifact.content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  // --- Render ---
  return (
    <div className="flex h-full w-full overflow-hidden relative" style={{ backgroundColor: 'var(--color-surface)' }}>
      {/* Expand sidebar button when collapsed */}
      {messagesWithArtifacts.length > 0 && !showSidebar && (
        <button
          onClick={() => setShowSidebar(true)}
          className="absolute left-0 top-[22px] z-20 p-2 bg-white border border-l-0 rounded-r-lg shadow-sm text-gray-500 hover:text-gray-700 hover:bg-gray-50 cursor-pointer flex items-center justify-center"
          style={{ borderColor: 'var(--color-border)', width: '32px', height: '32px' }}
          title="Expand Documents"
        >
          <ChevronsRight size={16} />
        </button>
      )}

      {/* Sidebar for Artifacts */}
      {messagesWithArtifacts.length > 0 && showSidebar && (
        <div 
          className="w-48 md:w-56 border-r flex flex-col flex-shrink-0 bg-[#f8fafc] transition-all"
          style={{ borderColor: 'var(--color-border)' }}
        >
          <div className="px-4 py-4 border-b flex justify-between items-center" style={{ borderColor: 'var(--color-border)' }}>
            <div>
              <h3 className="text-sm font-bold" style={{ color: 'var(--color-text)' }}>Documents</h3>
              <p className="text-xs" style={{ color: 'var(--color-text-dim)' }}>{messagesWithArtifacts.length} in this chat</p>
            </div>
            <button 
              onClick={() => setShowSidebar(false)} 
              className="p-1 rounded hover:bg-gray-200 text-gray-400 hover:text-gray-600 transition-colors cursor-pointer"
              title="Collapse Documents"
            >
              <ChevronsLeft size={16} />
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-2 flex flex-col gap-1">
            {messagesWithArtifacts.map((msg) => (
              <button
                key={msg.id}
                onClick={() => {
                  if (msg.artifact) onSelectArtifact(msg.artifact);
                }}
                className="flex items-center gap-2.5 p-2.5 rounded-lg text-left transition-all cursor-pointer"
                style={{
                  backgroundColor: activeArtifact === msg.artifact ? 'white' : 'transparent',
                  boxShadow: activeArtifact === msg.artifact ? '0 1px 2px rgba(0,0,0,0.05)' : 'none',
                  border: '1px solid',
                  borderColor: activeArtifact === msg.artifact ? 'rgba(79,70,229,0.2)' : 'transparent',
                }}
                onMouseEnter={e => {
                  if (activeArtifact !== msg.artifact) {
                    e.currentTarget.style.backgroundColor = 'rgba(0,0,0,0.03)';
                  }
                }}
                onMouseLeave={e => {
                  if (activeArtifact !== msg.artifact) {
                    e.currentTarget.style.backgroundColor = 'transparent';
                  }
                }}
              >
                <div className="w-6 h-6 rounded flex items-center justify-center flex-shrink-0" style={{ backgroundColor: activeArtifact === msg.artifact ? 'rgba(79,70,229,0.1)' : 'rgba(0,0,0,0.05)' }}>
                  <FileText size={12} style={{ color: activeArtifact === msg.artifact ? 'var(--color-primary)' : 'var(--color-text-dim)' }} />
                </div>
                <div className="flex flex-col min-w-0">
                  <span className="text-xs font-semibold truncate" style={{ color: activeArtifact === msg.artifact ? '#1a1f36' : 'var(--color-text)' }}>
                    {msg.artifact?.title || 'Untitled Document'}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 relative">
        {/* Loading Overlay */}
        {isLoading && (
          <div className="absolute inset-0 z-10 flex flex-col p-6 space-y-4" style={{ backgroundColor: 'var(--color-surface)' }}>
            <div className="flex items-center gap-2 mb-2">
              <Code size={16} style={{ color: 'var(--color-primary-light)' }} />
              <h3 className="text-sm font-medium" style={{ color: 'var(--color-text)' }}>
                Generating document...
              </h3>
            </div>
            <div className="skeleton h-8 w-3/4 rounded" />
            <div className="skeleton h-4 w-full rounded" />
            <div className="skeleton h-4 w-5/6 rounded" />
            <div className="skeleton h-4 w-4/5 rounded" />
            <div className="skeleton h-6 w-1/2 rounded mt-6" />
            <div className="skeleton h-4 w-full rounded" />
            <div className="skeleton h-4 w-3/4 rounded" />
          </div>
        )}

        {/* Empty state when no active artifact */}
        {!activeArtifact && !isLoading ? (
          <div className="flex flex-col items-center justify-center h-full p-8 text-center">
            <FileText size={48} style={{ color: 'var(--color-surface-lighter)' }} />
            <p className="mt-4 text-sm font-medium" style={{ color: 'var(--color-text)' }}>
              No artifact selected
            </p>
            <p className="mt-1 text-xs" style={{ color: 'var(--color-text-dim)' }}>
              Select an artifact from the sidebar, or request a new document.
            </p>
          </div>
        ) : activeArtifact && (
          <>
            {/* Header */}
            <div
              className="flex items-center justify-between px-6 py-4 border-b"
              style={{ borderColor: 'var(--color-border)' }}
            >
              <div className="flex flex-col gap-1 min-w-0">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" style={{ backgroundColor: 'rgba(79, 70, 229, 0.08)' }}>
                    <FileText size={18} style={{ color: 'var(--color-primary)' }} />
                  </div>
                  <h3 className="text-[17px] font-bold truncate tracking-tight" style={{ color: '#1a1f36' }}>
                    {activeArtifact.title || 'Artifact'}
                  </h3>
                </div>
                {(() => {
                  const activeMsg = messagesWithArtifacts.find(m => m.artifact === activeArtifact);
                  const dateStr = activeMsg?.created_at ? new Date(activeMsg.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }) : 'Unknown Date';
                  return (
                    <div className="flex items-center gap-1.5 ml-[40px]">
                      <div className="w-2 h-2 rounded-full bg-[#10b981]"></div>
                      <span className="text-[13px] font-medium" style={{ color: '#94a3b8' }}>
                        Generated • {dateStr}
                      </span>
                    </div>
                  );
                })()}
              </div>
              <div className="flex items-center gap-2 flex-shrink-0 ml-4">
                <button
                  onClick={handleDownload}
                  className="w-9 h-9 flex items-center justify-center rounded-lg transition-colors cursor-pointer bg-gray-50 border border-gray-100 text-gray-600 hover:bg-gray-100"
                  title="Download Document"
                >
                  <Download size={16} />
                </button>
                <button
                  onClick={handleCopy}
                  className="w-9 h-9 flex items-center justify-center rounded-lg transition-colors cursor-pointer bg-gray-50 border border-gray-100 text-gray-600 hover:bg-gray-100"
                  title="Copy Document"
                >
                  {copied ? <Check size={16} className="text-green-500" /> : <Copy size={16} />}
                </button>
                <button
                  onClick={onClose}
                  className="w-9 h-9 flex items-center justify-center rounded-lg transition-colors cursor-pointer bg-gray-50 border border-gray-100 text-gray-600 hover:bg-gray-100"
                  aria-label="Close document viewer"
                  title="Close Essay"
                >
                  <X size={18} />
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6 flex flex-col">
              <div className="flex-1">
                {activeArtifact.type === 'html' ? (
                  <HtmlRenderer content={activeArtifact.content} />
                ) : (
                  <div className="markdown-content">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{activeArtifact.content}</ReactMarkdown>
                  </div>
                )}
              </div>

            </div>
          </>
        )}
      </div>
    </div>
  );
}

// --- Helper components ---

function ActionButton({
  icon,
  label,
  onClick,
}: {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-1 px-2 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 cursor-pointer"
      style={{ color: 'var(--color-text-dim)' }}
      onMouseEnter={e => {
        e.currentTarget.style.backgroundColor = 'var(--color-surface-lighter)';
        e.currentTarget.style.color = 'var(--color-primary)';
      }}
      onMouseLeave={e => {
        e.currentTarget.style.backgroundColor = 'transparent';
        e.currentTarget.style.color = 'var(--color-text-dim)';
      }}
      title={label}
    >
      {icon}
      <span className="hidden lg:inline">{label}</span>
    </button>
  );
}

/**
 * Renders HTML content in a sandboxed iframe.
 *
 * Security strategy:
 * - Uses sandbox attribute WITHOUT allow-same-origin
 * - This prevents the iframe from accessing the parent window's DOM,
 *   cookies, localStorage, or any other origin-specific data
 * - Content is injected via srcdoc (no network request)
 * - allow-scripts is omitted to block JavaScript execution entirely
 */
function HtmlRenderer({ content }: { content: string }) {
  let cleanContent = content;
  
  // Extract content from inside ```html ... ``` if the LLM wrapped it in a code block
  const match = content.match(/```(?:html)?\s*([\s\S]*?)\s*```/i);
  if (match) {
    cleanContent = match[1];
  } else {
    // Fallback if it just starts with ```html but lacks closing
    cleanContent = content.replace(/^```(?:html)?\s*/i, '').replace(/```\s*$/, '');
  }

  // Validate content is actually HTML-like
  if (!cleanContent || (!cleanContent.includes('<') && !cleanContent.includes('>'))) {
    return (
      <div className="p-4 rounded-lg" style={{ backgroundColor: 'var(--color-surface-light)' }}>
        <p className="text-sm" style={{ color: 'var(--color-error)' }}>
          Invalid HTML content
        </p>
      </div>
    );
  }

  return (
    <iframe
      srcDoc={cleanContent}
      sandbox=""
      title="Artifact HTML content"
      className="w-full rounded-lg border"
      style={{
        height: '100%',
        minHeight: '500px',
        backgroundColor: 'white',
        borderColor: 'var(--color-border)',
      }}
    />
  );
}
