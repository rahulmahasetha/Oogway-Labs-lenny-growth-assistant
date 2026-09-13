/* ArtifactViewer — renders Markdown or HTML artifacts with actions */

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { X, FileText, Code, Copy, Check, Download, RefreshCw } from 'lucide-react';
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
    <div className="flex h-full w-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface)' }}>
      {/* Sidebar for Artifacts */}
      {messagesWithArtifacts.length > 0 && (
        <div 
          className="w-56 border-r flex flex-col flex-shrink-0 bg-[#f8fafc]"
          style={{ borderColor: 'var(--color-border)' }}
        >
          <div className="px-4 py-4 border-b" style={{ borderColor: 'var(--color-border)' }}>
            <h3 className="text-sm font-bold" style={{ color: 'var(--color-text)' }}>Documents</h3>
            <p className="text-xs" style={{ color: 'var(--color-text-dim)' }}>{messagesWithArtifacts.length} in this chat</p>
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
              <button
                onClick={onClose}
                className="p-2 rounded-lg transition-colors cursor-pointer flex-shrink-0 ml-4"
                style={{ color: 'var(--color-text-dim)' }}
                onMouseEnter={e => e.currentTarget.style.backgroundColor = 'var(--color-surface-lighter)'}
                onMouseLeave={e => e.currentTarget.style.backgroundColor = 'transparent'}
                aria-label="Close document viewer"
                title="Close Essay"
              >
                <X size={20} />
              </button>
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

              {/* Bottom Actions */}
              <div className="mt-8 pt-4 border-t flex justify-end" style={{ borderColor: 'var(--color-border)' }}>
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-[14px] font-semibold transition-all duration-200 cursor-pointer border"
                  style={{
                    backgroundColor: 'white',
                    color: '#4f46e5',
                    borderColor: '#a5b4fc',
                    boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.backgroundColor = '#f0f3ff';
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.backgroundColor = 'white';
                  }}
                >
                  {copied ? <Check size={16} /> : <Copy size={16} />}
                  {copied ? 'Copied to Clipboard' : 'Copy Document'}
                </button>
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
  // Validate content is actually HTML-like
  if (!content || (!content.includes('<') && !content.includes('>'))) {
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
      srcDoc={content}
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
