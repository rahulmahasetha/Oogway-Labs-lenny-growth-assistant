/* Main App — orchestrates sidebar, chat, and artifact viewer */

import { useState, useCallback, useEffect } from 'react';
import { QueryClient, QueryClientProvider, useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { PanelRightOpen, PanelRightClose, Menu, X } from 'lucide-react';
import { Sidebar } from './components/Sidebar';
import { ChatArea } from './components/ChatArea';
import { ArtifactViewer } from './components/ArtifactViewer';
import * as api from './api/client';
import type { Artifact, Message, Session, SessionDetail, AppConfig } from './types';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, refetchOnWindowFocus: false },
  },
});

function AppContent() {
  const qc = useQueryClient();
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [activeArtifact, setActiveArtifact] = useState<Artifact | null>(null);
  const [showArtifact, setShowArtifact] = useState(false);
  const [showMobileSidebar, setShowMobileSidebar] = useState(false);
  const [isIngesting, setIsIngesting] = useState(false);


  const { data: sessions = [] } = useQuery<Session[]>({
    queryKey: ['sessions'],
    queryFn: api.listSessions,
  });

  const { data: activeSession } = useQuery<SessionDetail>({
    queryKey: ['session', activeSessionId],
    queryFn: () => api.getSession(activeSessionId!),
    enabled: !!activeSessionId,
  });

  const { data: config } = useQuery<AppConfig>({
    queryKey: ['config'],
    queryFn: api.getConfig,
  });


  const createSessionMutation = useMutation({
    mutationFn: api.createSession,
    onSuccess: (session) => {
      qc.invalidateQueries({ queryKey: ['sessions'] });
      setActiveSessionId(session.id);
      setShowMobileSidebar(false);
    },
  });

  const deleteSessionMutation = useMutation({
    mutationFn: api.deleteSession,
    onSuccess: (_, sessionId) => {
      qc.invalidateQueries({ queryKey: ['sessions'] });
      if (activeSessionId === sessionId) {
        setActiveSessionId(null);
      }
    },
  });

  const updateSessionMutation = useMutation({
    mutationFn: ({ id, title }: { id: string; title: string }) => api.updateSession(id, title),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['sessions'] });
      qc.invalidateQueries({ queryKey: ['session', activeSessionId] });
    },
  });

  const sendMessageMutation = useMutation({
    mutationFn: ({ sessionId, content }: { sessionId: string; content: string }) =>
      api.sendMessage(sessionId, content),
    onMutate: async ({ sessionId, content }) => {
      // Optimistic update: add user message immediately
      await qc.cancelQueries({ queryKey: ['session', sessionId] });
      const previous = qc.getQueryData<SessionDetail>(['session', sessionId]);
      if (previous) {
        const optimisticMsg: Message = {
          id: `temp-${Date.now()}`,
          session_id: sessionId,
          role: 'user',
          content,
          created_at: new Date().toISOString(),
        };
        qc.setQueryData<SessionDetail>(['session', sessionId], {
          ...previous,
          messages: [...previous.messages, optimisticMsg],
        });
      }
      return { previous };
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['session', activeSessionId] });
      qc.invalidateQueries({ queryKey: ['sessions'] });
    },
    onError: (_err, variables, context) => {
      if (context?.previous) {
        qc.setQueryData(['session', variables.sessionId], context.previous);
      }
    },
  });

  // Auto-open artifact panel when a new artifact arrives
  useEffect(() => {
    if (!activeSession?.messages) return;
    const msgs = activeSession.messages;
    const lastMsg = msgs[msgs.length - 1];
    if (lastMsg?.artifact && lastMsg.role === 'assistant') {
      setActiveArtifact(lastMsg.artifact);
      setShowArtifact(true);
    }
  }, [activeSession?.messages]);

  // Isolate artifacts per session
  useEffect(() => {
    setActiveArtifact(null);
    setShowArtifact(false);
  }, [activeSessionId]);

  const handleNewChat = useCallback(() => {
    createSessionMutation.mutate();
  }, [createSessionMutation]);

  const handleSend = useCallback(
    (content: string) => {
      if (!activeSessionId) return;
      sendMessageMutation.mutate({ sessionId: activeSessionId, content });
    },
    [activeSessionId, sendMessageMutation]
  );

  const handleViewArtifact = useCallback((message: Message) => {
    if (message.artifact) {
      setActiveArtifact(message.artifact);
      setShowArtifact(true);
    }
  }, []);

  const handleIngest = useCallback(async () => {
    setIsIngesting(true);
    try {
      await api.runIngestion();
    } catch (e) {
      console.error('Ingestion failed:', e);
    } finally {
      setIsIngesting(false);
    }
  }, []);

  return (
    <div className="flex h-screen overflow-hidden" style={{ backgroundColor: 'var(--color-surface)' }}>
      {/* Mobile sidebar overlay */}
      {showMobileSidebar && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={() => setShowMobileSidebar(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`${
          showMobileSidebar ? 'fixed inset-y-0 left-0 z-50' : 'hidden'
        } md:relative md:flex`}
      >
        <Sidebar
          sessions={sessions}
          activeSessionId={activeSessionId}
          config={config ?? null}
          onSelectSession={(id) => {
            setActiveSessionId(id);
            setShowMobileSidebar(false);
          }}
          onNewChat={handleNewChat}
          onDeleteSession={(id) => deleteSessionMutation.mutate(id)}
          onUpdateSession={(id, title) => updateSessionMutation.mutate({ id, title })}
          onIngest={handleIngest}
          isIngesting={isIngesting}
        />
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile header */}
        <div
          className="flex items-center justify-between px-4 py-3 md:hidden border-b"
          style={{ borderColor: 'var(--color-border)' }}
        >
          <button
            onClick={() => setShowMobileSidebar(true)}
            className="p-2 rounded-lg cursor-pointer"
            style={{ color: 'var(--color-text-muted)' }}
            aria-label="Open sidebar"
          >
            <Menu size={20} />
          </button>
          <h1
            className="text-sm font-bold"
            style={{
              background: 'linear-gradient(135deg, var(--color-primary-light), var(--color-accent))',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            Lenny Growth Assistant
          </h1>
          <button
            onClick={() => setShowArtifact(!showArtifact)}
            className="p-2 rounded-lg cursor-pointer"
            style={{ color: showArtifact ? 'var(--color-primary)' : 'var(--color-text-muted)' }}
            aria-label={showArtifact ? 'Hide artifact panel' : 'Show artifact panel'}
          >
            {showArtifact ? <PanelRightClose size={20} /> : <PanelRightOpen size={20} />}
          </button>
        </div>

        {/* Chat + Artifact split */}
        <div className="flex-1 flex overflow-hidden">
          {/* Chat area */}
          <div className="flex-1 flex flex-col min-w-0">
            {/* Desktop artifact toggle */}
            <div
              className="hidden md:flex items-center justify-end px-4 py-2 border-b"
              style={{ borderColor: 'var(--color-border)' }}
            >
              <button
                onClick={() => setShowArtifact(!showArtifact)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 cursor-pointer shadow-sm"
                style={{
                  background: showArtifact 
                    ? 'linear-gradient(135deg, var(--color-primary), var(--color-accent))' 
                    : 'rgba(79, 70, 229, 0.05)',
                  color: showArtifact ? 'white' : 'var(--color-primary)',
                  border: '1px solid',
                  borderColor: showArtifact ? 'transparent' : 'rgba(79, 70, 229, 0.2)',
                }}
                aria-label={showArtifact ? 'Hide artifact viewer' : 'Show artifact viewer'}
              >
                {showArtifact ? <PanelRightClose size={14} /> : <PanelRightOpen size={14} />}
                Artifact Viewer
              </button>
            </div>

            <ChatArea
              messages={activeSession?.messages ?? []}
              isLoading={sendMessageMutation.isPending}
              onSend={handleSend}
              onViewArtifact={handleViewArtifact}
              hasSession={!!activeSessionId}
              onNewChat={handleNewChat}
            />
          </div>

          {/* Artifact viewer panel */}
          {showArtifact && (
            <div
              className="border-l"
              style={{
                width: '45%',
                minWidth: '350px',
                borderColor: 'var(--color-border)',
              }}
            >
              <ArtifactViewer
                messagesWithArtifacts={activeSession?.messages.filter(m => m.artifact) || []}
                activeArtifact={activeArtifact}
                onSelectArtifact={setActiveArtifact}
                onClose={() => setShowArtifact(false)}
                onRegenerate={() => {
                  if (activeSessionId) {
                    sendMessageMutation.mutate({
                      sessionId: activeSessionId,
                      content: 'Regenerate the document with the same topic but improved content.',
                    });
                  }
                }}
                isLoading={sendMessageMutation.isPending && showArtifact}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  );
}
