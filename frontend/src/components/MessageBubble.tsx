/* MessageBubble — renders a single chat message with optional sources */

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ExternalLink, FileText, User, Bot, Copy, Check } from 'lucide-react';
import type { Message } from '../types';

interface MessageBubbleProps {
  message: Message;
  onViewArtifact?: (message: Message) => void;
}

export function MessageBubble({ message, onViewArtifact }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`flex gap-3 animate-fade-in w-full min-w-0 ${isUser ? 'justify-end' : ''}`}>
      {/* Avatar */}
      {!isUser && (
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-1"
          style={{
            background: 'linear-gradient(135deg, var(--color-primary), var(--color-primary-dark))',
          }}
        >
          <Bot size={16} color="white" />
        </div>
      )}

      <div className={`flex flex-col gap-2 ${isUser ? 'items-end' : 'w-full'} min-w-0`} style={{ maxWidth: isUser ? '85%' : '100%' }}>
        {/* Message content */}
        <div
          className="px-4 py-3 rounded-2xl text-sm min-w-0 overflow-x-auto"
          style={{
            backgroundColor: isUser ? 'var(--color-primary)' : 'var(--color-surface-light)',
            color: isUser ? 'white' : 'var(--color-text)',
            borderBottomRightRadius: isUser ? '4px' : undefined,
            borderBottomLeftRadius: !isUser ? '4px' : undefined,
          }}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="markdown-content">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {/* Actions (Copy & Artifact) */}
        <div className={`flex items-center gap-2 mt-1 ${isUser ? 'justify-end' : 'justify-start'}`}>
          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-2 py-1 rounded text-xs font-medium transition-all duration-200 cursor-pointer"
            style={{ color: 'var(--color-text-dim)', backgroundColor: 'transparent' }}
            onMouseEnter={e => (e.currentTarget.style.backgroundColor = 'var(--color-surface-lighter)')}
            onMouseLeave={e => (e.currentTarget.style.backgroundColor = 'transparent')}
            title="Copy message text"
          >
            {copied ? <Check size={12} /> : <Copy size={12} />}
            {copied ? 'Copied!' : 'Copy'}
          </button>
          
          {message.artifact && onViewArtifact && (
            <button
              onClick={() => onViewArtifact(message)}
              className="flex items-center gap-2 px-3 py-1 rounded-lg text-xs font-medium transition-all duration-200 cursor-pointer"
              style={{
                backgroundColor: 'var(--color-surface-light)',
                border: '1px solid var(--color-primary)',
                color: 'var(--color-primary-light)',
              }}
              onMouseEnter={e => (e.currentTarget.style.backgroundColor = 'var(--color-surface-lighter)')}
              onMouseLeave={e => (e.currentTarget.style.backgroundColor = 'var(--color-surface-light)')}
            >
              <FileText size={14} />
              View {message.artifact.title || 'Artifact'}
            </button>
          )}
        </div>

        {/* Source citations */}
        {message.sources && message.sources.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-1">
            {message.sources.map((source, idx) => (
              <a
                key={`${source.id}-${idx}`}
                href={source.post_url || '#'}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 px-2 py-1 rounded-md text-xs transition-all duration-150"
                style={{
                  backgroundColor: 'var(--color-surface-lighter)',
                  color: 'var(--color-text-muted)',
                  textDecoration: 'none',
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.backgroundColor = 'var(--color-primary)';
                  e.currentTarget.style.color = 'white';
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.backgroundColor = 'var(--color-surface-lighter)';
                  e.currentTarget.style.color = 'var(--color-text-muted)';
                }}
                title={source.title}
              >
                <ExternalLink size={10} />
                <span className="truncate" style={{ maxWidth: '180px' }}>
                  {source.guest || source.title.slice(0, 30)}
                </span>
              </a>
            ))}
          </div>
        )}
      </div>

      {/* User avatar */}
      {isUser && (
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-1"
          style={{ backgroundColor: 'var(--color-surface-lighter)' }}
        >
          <User size={16} style={{ color: 'var(--color-text-muted)' }} />
        </div>
      )}
    </div>
  );
}
