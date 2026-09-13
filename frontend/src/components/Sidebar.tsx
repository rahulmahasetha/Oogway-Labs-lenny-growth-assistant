/* Sidebar — session list with new chat button and provider badge */

import { useState } from 'react';
import { Plus, MessageSquare, Trash2, Database, Loader2, Pencil, Home, FileText, ChevronDown, CheckCircle, Sparkles } from 'lucide-react';
import type { AppConfig, Session } from '../types';

interface SidebarProps {
  sessions: Session[];
  activeSessionId: string | null;
  config: AppConfig | null;
  onSelectSession: (id: string | null) => void;
  onNewChat: () => void;
  onDeleteSession: (id: string) => void;
  onUpdateSession: (id: string, title: string) => void;
  onIngest: () => void;
  isIngesting: boolean;
}

export function Sidebar({
  sessions,
  activeSessionId,
  config,
  onSelectSession,
  onNewChat,
  onDeleteSession,
  onUpdateSession,
  onIngest,
  isIngesting,
}: SidebarProps) {
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');

  return (
    <aside
      className="flex flex-col h-full border-r w-[260px] md:w-[280px] flex-shrink-0"
      style={{
        backgroundColor: 'var(--color-surface)',
        borderColor: 'var(--color-border)',
      }}
    >
      <div 
        className="p-4 flex items-center gap-3 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={() => onSelectSession(null)}
      >
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
          style={{ background: 'linear-gradient(135deg, var(--color-primary), var(--color-accent))' }}
        >
          <Sparkles size={20} color="white" />
        </div>
        <div className="flex-1 min-w-0">
          <h1 className="text-sm font-bold text-gray-900 truncate">Lenny Growth Assistant</h1>
          <p className="text-xs text-gray-500 truncate">Powered by Lenny's Podcast</p>
        </div>
      </div>

      {/* New Chat Button */}
      <div className="px-4 pb-4">
        <button
          onClick={onNewChat}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 cursor-pointer shadow-sm hover:shadow-md"
          style={{
            backgroundColor: 'var(--color-primary)',
            color: 'white',
          }}
          aria-label="Start new chat"
        >
          <Plus size={18} />
          <span className="text-base font-semibold">New Chat</span>
        </button>
      </div>

      {/* Main Navigation */}
      <nav className="px-3 pb-4 space-y-1">
        <button
          onClick={onNewChat}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors cursor-pointer"
          style={{ backgroundColor: 'rgba(79, 70, 229, 0.08)', color: 'var(--color-primary-dark)' }}
        >
          <Home size={18} />
          <span className="text-base font-semibold">Home</span>
        </button>
      </nav>

      {/* Session List */}
      <div className="flex-1 overflow-y-auto px-3 pb-3">
        <div className="flex items-center justify-between px-3 py-2 mb-1">
          <h3 className="text-sm font-medium text-gray-600">Recent Chats</h3>
          <button className="text-xs font-semibold text-indigo-600 hover:text-indigo-700 cursor-pointer">
            See all
          </button>
        </div>
        
        {sessions.length === 0 && (
          <p className="text-center py-4 text-xs text-gray-400">
            No conversations yet
          </p>
        )}
        
        {sessions.map(session => (
          <div
            key={session.id}
            className="group flex items-start gap-3 px-3 py-2 rounded-xl mb-1 cursor-pointer transition-colors"
            style={{
              backgroundColor: session.id === activeSessionId ? 'rgba(79, 70, 229, 0.04)' : 'transparent',
            }}
            onClick={() => onSelectSession(session.id)}
            onMouseEnter={e => {
              if (session.id !== activeSessionId)
                e.currentTarget.style.backgroundColor = 'var(--color-surface-light)';
            }}
            onMouseLeave={e => {
              if (session.id !== activeSessionId)
                e.currentTarget.style.backgroundColor = 'transparent';
            }}
          >
            <MessageSquare size={18} className="mt-0.5 text-gray-600 flex-shrink-0" style={{ color: session.id === activeSessionId ? 'var(--color-primary)' : '#4b5563' }} />
            <div className="flex-1 min-w-0 flex flex-col">
              {editingSessionId === session.id ? (
                <input
                  type="text"
                  className="w-full text-sm bg-white border border-gray-300 rounded px-1 outline-none"
                  value={editTitle}
                  onChange={e => setEditTitle(e.target.value)}
                  onBlur={() => {
                    if (editTitle.trim() && editTitle !== session.title) {
                      onUpdateSession(session.id, editTitle.trim());
                    }
                    setEditingSessionId(null);
                  }}
                  onKeyDown={e => {
                    if (e.key === 'Enter') {
                      if (editTitle.trim() && editTitle !== session.title) {
                        onUpdateSession(session.id, editTitle.trim());
                      }
                      setEditingSessionId(null);
                    }
                    if (e.key === 'Escape') {
                      setEditingSessionId(null);
                    }
                  }}
                  autoFocus
                  onClick={e => e.stopPropagation()}
                />
              ) : (
                <span className="text-sm truncate font-medium text-gray-700" style={{ color: session.id === activeSessionId ? 'var(--color-primary-dark)' : '#374151' }}>
                  {session.title}
                </span>
              )}
              <span className="text-xs text-gray-400">
                {new Date(session.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
              </span>
            </div>
            
            {editingSessionId !== session.id && (
              <div className="opacity-0 group-hover:opacity-100 flex items-center transition-opacity ml-1">
                <button
                  onClick={e => {
                    e.stopPropagation();
                    setEditingSessionId(session.id);
                    setEditTitle(session.title);
                  }}
                  className="p-1 rounded text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <Pencil size={14} />
                </button>
                <button
                  onClick={e => {
                    e.stopPropagation();
                    onDeleteSession(session.id);
                  }}
                  className="p-1 rounded text-red-400 hover:text-red-600 transition-colors"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Footer — Provider badge */}
      <div className="p-4 bg-gray-50/50 mt-auto">
        <button
          onClick={onIngest}
          disabled={isIngesting}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs font-medium mb-3 transition-all cursor-pointer border border-gray-200 bg-white shadow-sm hover:bg-gray-50 disabled:opacity-50"
        >
          {isIngesting ? <Loader2 size={12} className="animate-spin text-gray-500" /> : <Database size={12} className="text-gray-500" />}
          <span className="text-gray-700">{isIngesting ? 'Ingesting...' : 'Ingest Transcripts'}</span>
        </button>

        {config && (
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-3 flex flex-col gap-1 cursor-pointer hover:bg-gray-100 transition-colors">
            <span className="text-xs text-gray-500 font-medium">AI Model</span>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full bg-emerald-500"></div>
                <span className="text-sm font-semibold text-gray-800 truncate">
                  {config.llm_provider.toUpperCase()} ({config.llm_model})
                </span>
              </div>
              <ChevronDown size={16} className="text-gray-500" />
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}
