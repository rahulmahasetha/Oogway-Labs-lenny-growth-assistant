/* ChatArea — main chat display area with messages and composer */

import { useEffect, useRef } from 'react';
import { Sparkles, BookOpen, FileText, PenTool, Plus, CheckCircle2, MessageSquare, ArrowRight } from 'lucide-react';
import { MessageBubble } from './MessageBubble';
import { MessageComposer } from './MessageComposer';
import type { Message } from '../types';

interface ChatAreaProps {
  messages: Message[];
  isLoading: boolean;
  onSend: (content: string) => void;
  onViewArtifact: (message: Message) => void;
  hasSession: boolean;
  onNewChat?: () => void;
}

export function ChatArea({ messages, isLoading, onSend, onViewArtifact, hasSession, onNewChat }: ChatAreaProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  if (!hasSession) {
    return <WelcomeScreen onNewChat={onNewChat} />;
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {messages.length === 0 && !isLoading && (
          <div className="flex flex-col items-center justify-center h-full">
            <Sparkles size={32} style={{ color: 'var(--color-primary-light)' }} />
            <p className="mt-3 text-sm" style={{ color: 'var(--color-text-muted)' }}>
              Ask anything about product management, growth, or AI
            </p>
            <div className="flex flex-wrap justify-center gap-2 mt-4 max-w-lg">
              {STARTER_PROMPTS.map((prompt, i) => (
                <button
                  key={i}
                  onClick={() => onSend(prompt)}
                  className="px-3 py-2 rounded-lg text-xs transition-all duration-200 cursor-pointer"
                  style={{
                    backgroundColor: 'var(--color-surface-light)',
                    border: '1px solid var(--color-border)',
                    color: 'var(--color-text-muted)',
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.borderColor = 'var(--color-primary)';
                    e.currentTarget.style.color = 'var(--color-primary-light)';
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.borderColor = 'var(--color-border)';
                    e.currentTarget.style.color = 'var(--color-text-muted)';
                  }}
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="space-y-6 max-w-5xl mx-auto">
          {messages.map(msg => (
            <MessageBubble
              key={msg.id}
              message={msg}
              onViewArtifact={onViewArtifact}
            />
          ))}

          {/* Loading indicator */}
          {isLoading && (
            <div className="flex gap-3 animate-fade-in">
              <div
                className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                style={{
                  background: 'linear-gradient(135deg, var(--color-primary), var(--color-primary-dark))',
                }}
              >
                <Sparkles size={16} color="white" />
              </div>
              <div
                className="px-4 py-3 rounded-2xl"
                style={{
                  backgroundColor: 'var(--color-surface-light)',
                  borderBottomLeftRadius: '4px',
                }}
              >
                <div className="flex gap-1.5">
                  <span className="loading-dot" />
                  <span className="loading-dot" />
                  <span className="loading-dot" />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Composer */}
      <MessageComposer onSend={onSend} isLoading={isLoading} />
    </div>
  );
}

function WelcomeScreen({ onNewChat }: { onNewChat?: () => void }) {
  return (
    <div className="flex flex-col items-center w-full h-full bg-[#fafcff] overflow-y-auto px-6 py-6" style={{ fontFamily: 'var(--font-sans)' }}>
      <div className="max-w-[1200px] w-full flex flex-col pt-0 pb-4 h-full justify-center">
        
        {/* TOP SECTION: Text on Left, Illustration on Right */}
        <div className="flex flex-col lg:flex-row gap-8 items-center lg:items-center mb-8">
          
          {/* Left Text Column */}
          <div className="flex-1 flex flex-col items-start w-full mt-4">
            <h1 className="text-4xl md:text-[56px] font-extrabold mb-4 leading-[1.1] tracking-tight" style={{ color: '#1a1f36' }}>
              Lenny Growth<br />Assistant
            </h1>
            
            <p className="text-lg mb-5 leading-relaxed max-w-[550px]" style={{ color: '#4b5563' }}>
              Your AI-powered product management advisor, grounded in exclusive insights from <strong>Lenny's Podcast</strong> and Newsletter.
            </p>

            <div className="flex flex-wrap items-center gap-5 text-[14px] font-semibold" style={{ color: '#4b5563' }}>
              <span className="flex items-center gap-2"><CheckCircle2 size={18} className="text-[#10b981]" /> Trusted insights</span>
              <span className="flex items-center gap-2"><CheckCircle2 size={18} className="text-[#10b981]" /> Actionable strategies</span>
              <span className="flex items-center gap-2"><CheckCircle2 size={18} className="text-[#10b981]" /> Better products</span>
            </div>
          </div>

          {/* Right Illustration Column */}
          <div className="hidden lg:flex flex-1 items-center justify-center relative w-full h-[320px]">
            {/* Soft background glow */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] bg-blue-100/40 rounded-full blur-[60px]"></div>

            {/* Main Browser window */}
            <div className="relative z-10 w-[420px] bg-white rounded-[20px] shadow-[0_20px_50px_-12px_rgba(0,0,0,0.1)] border border-gray-100 overflow-hidden transform -rotate-2">
              {/* Top bar */}
              <div className="bg-[#4f46e5] h-6 w-full flex items-center px-4 gap-1.5">
                <div className="w-2 h-2 rounded-full bg-white/40"></div>
                <div className="w-2 h-2 rounded-full bg-white/40"></div>
                <div className="w-2 h-2 rounded-full bg-white/40"></div>
              </div>
              
              {/* Body */}
              <div className="px-6 py-6 flex h-[190px] bg-white">
                {/* Text column */}
                <div className="flex flex-col gap-2 items-center justify-center w-1/2 border-r border-gray-100 pr-4" style={{ fontFamily: '"Comic Sans MS", cursive, sans-serif' }}>
                  <div className="text-[20px] text-[#1e1b4b] font-medium tracking-tight">Ideas</div>
                  <div className="text-[#4f46e5] text-sm">↓</div>
                  <div className="text-[20px] text-[#1e1b4b] font-medium tracking-tight">Growth</div>
                  <div className="text-[#4f46e5] text-sm">↓</div>
                  <div className="text-[20px] text-[#1e1b4b] font-medium tracking-tight">Impact</div>
                </div>
                
                {/* Bar chart */}
                <div className="flex items-end justify-center gap-2 pl-6 pb-2 w-1/2 h-full">
                  <div className="w-4 bg-[#bfdbfe] rounded-t-sm h-[40%]"></div>
                  <div className="w-4 bg-[#60a5fa] rounded-t-sm h-[65%]"></div>
                  <div className="w-4 bg-[#3b82f6] rounded-t-sm h-[50%]"></div>
                  <div className="w-4 bg-[#4f46e5] rounded-t-sm h-[85%]"></div>
                </div>
              </div>
            </div>
            
            {/* Sticky Notes */}
            <div className="absolute top-[5%] left-[0px] z-20 w-[90px] h-[100px] shadow-lg transform -rotate-6 p-3 text-[12px] leading-relaxed flex flex-col justify-center" style={{ backgroundColor: '#f3e8ff', color: '#4c1d95', fontFamily: '"Comic Sans MS", cursive, sans-serif' }}>
              Build<br/>Ship<br/>Learn<br/>Repeat
            </div>
            
            <div className="absolute bottom-[5%] right-[0px] z-20 w-[100px] h-[110px] shadow-lg transform rotate-3 p-3 text-[12px] leading-relaxed flex flex-col justify-center" style={{ backgroundColor: '#d1fae5', color: '#065f46', fontFamily: '"Comic Sans MS", cursive, sans-serif' }}>
              Better<br/>Products<br/>Happier<br/>Users
            </div>
          </div>
        </div>
        
        {/* MIDDLE SECTION: 3 Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full mb-8">
          <FeatureCard 
            icon={<MessageSquare size={20} className="text-[#5b45e6]" />}
            iconBg="#f0eefe"
            title="Ask Anything"
            description="Query the vast archive of Lenny's podcasts and newsletters. Get practical advice and real-world examples."
            tags={['Product', 'Growth', 'Strategy']}
            borderColor="#e0e7ff"
            shadowColor="rgba(91, 69, 230, 0.08)"
            textColor="#5b45e6"
          />
          <FeatureCard 
            icon={<FileText size={20} className="text-[#0ea5e9]" />}
            iconBg="#e0f2fe"
            title="Create Documents"
            description="Draft detailed product specs, go-to-market plans, and competitive analysis reports."
            tags={['PRD', 'Strategy', 'Analysis']}
            borderColor="#bae6fd"
            shadowColor="rgba(14, 165, 233, 0.08)"
            textColor="#0ea5e9"
          />
          <FeatureCard 
            icon={<PenTool size={20} className="text-[#10b981]" />}
            iconBg="#d1fae5"
            title="Write Essays"
            description="Generate high-quality, structured essays inspired by the Ship 30 for 30 framework."
            tags={['Essays', 'Frameworks', 'Ideas']}
            borderColor="#a7f3d0"
            shadowColor="rgba(16, 185, 129, 0.08)"
            textColor="#10b981"
          />
        </div>
        
        {/* BOTTOM SECTION: CTA & Quote */}
        <div className="flex flex-col items-center justify-center w-full">
          <button
            onClick={onNewChat}
            className="px-8 py-3 rounded-full font-semibold text-[14px] transition-all duration-300 hover:shadow-lg hover:-translate-y-0.5 flex items-center justify-center gap-2 cursor-pointer shadow-md mb-4"
            style={{
              backgroundColor: '#5b45e6',
              color: 'white',
            }}
          >
            <Plus size={16} />
            Start Your First Chat
            <Sparkles size={14} className="opacity-80" />
          </button>
          
          <p className="text-[13px] font-medium mb-3 text-center" style={{ color: '#64748b' }}>
            Turn ideas into action with the power of Lenny's insights.
          </p>
          
          <p className="text-[12px] italic text-center" style={{ color: '#94a3b8' }}>
            "Better products start with better questions."<br/>
            — Lenny Rachitsky
          </p>
        </div>

      </div>
    </div>
  );
}

function FeatureCard({ icon, iconBg, title, description, tags, borderColor, shadowColor, textColor }: { icon: React.ReactNode, iconBg: string, title: string, description: string, tags: string[], borderColor: string, shadowColor: string, textColor: string }) {
  return (
    <div 
      className="p-5 rounded-[20px] bg-white flex flex-col hover:-translate-y-1 transition-all duration-300 cursor-default" 
      style={{ 
        border: `1px solid ${borderColor}`,
        boxShadow: `0 8px 30px -10px ${shadowColor}`
      }}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-[12px] flex items-center justify-center flex-shrink-0" style={{ backgroundColor: iconBg }}>
            {icon}
          </div>
          <h3 className="font-bold text-[15px] tracking-tight" style={{ color: '#1a1f36' }}>{title}</h3>
        </div>
        <div className="w-7 h-7 rounded-full border flex items-center justify-center" style={{ borderColor: borderColor, color: textColor }}>
          <ArrowRight size={14} strokeWidth={2.5} />
        </div>
      </div>
      <p className="text-[13px] leading-relaxed mb-4 flex-1" style={{ color: '#4b5563' }}>{description}</p>
      <div className="flex flex-wrap items-center gap-2">
        {tags.map(tag => (
          <span key={tag} className="px-2.5 py-1 rounded-full text-[11px] font-semibold" style={{ backgroundColor: iconBg, color: textColor }}>
            {tag}
          </span>
        ))}
      </div>
    </div>
  );
}

const STARTER_PROMPTS = [
  "How did Duolingo reignite user growth?",
  "What does Marc Andreessen think about AI?",
  "How are product teams evolving in 2026?",
  "Write an essay on growth strategies from Lenny's guests",
];
