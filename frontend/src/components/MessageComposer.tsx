/* MessageComposer — input area for sending messages */

import { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';

interface MessageComposerProps {
  onSend: (content: string) => void;
  isLoading: boolean;
  disabled?: boolean;
}

export function MessageComposer({ onSend, isLoading, disabled }: MessageComposerProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    }
  }, [input]);

  const handleSubmit = () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading || disabled) return;
    onSend(trimmed);
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="p-4" style={{ borderTop: '1px solid var(--color-border)' }}>
      <div
        className="flex items-end gap-2 rounded-xl px-4 py-3 transition-all duration-200"
        style={{
          backgroundColor: 'var(--color-surface-light)',
          border: '1px solid var(--color-border)',
        }}
        onFocus={e => (e.currentTarget.style.borderColor = 'var(--color-primary)')}
        onBlur={e => (e.currentTarget.style.borderColor = 'var(--color-border)')}
      >
        <textarea
          ref={textareaRef}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about product management, growth, or request a Ship 30 essay..."
          rows={1}
          disabled={isLoading || disabled}
          className="flex-1 resize-none bg-transparent outline-none text-sm min-w-0"
          style={{
            color: 'var(--color-text)',
            maxHeight: '200px',
          }}
          aria-label="Message input"
        />
        <button
          onClick={handleSubmit}
          disabled={!input.trim() || isLoading || disabled}
          className="p-2 rounded-lg transition-all duration-200 cursor-pointer disabled:opacity-30 disabled:cursor-not-allowed"
          style={{
            backgroundColor: input.trim() ? 'var(--color-primary)' : 'transparent',
            color: input.trim() ? 'white' : 'var(--color-text-dim)',
          }}
          aria-label="Send message"
        >
          {isLoading ? (
            <Loader2 size={18} className="animate-spin" />
          ) : (
            <Send size={18} />
          )}
        </button>
      </div>
      <p className="text-center mt-2 text-xs" style={{ color: 'var(--color-text-dim)' }}>
        Answers grounded in Lenny's Podcast transcripts & newsletters · Press Enter to send, Shift+Enter for new line
      </p>
    </div>
  );
}
