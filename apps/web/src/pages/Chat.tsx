import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Sparkles, 
  Send, 
  Paperclip, 
  Search, 
  BrainCircuit, 
  Mic, 
  Square, 
  Pin, 
  Trash2, 
  GitBranch, 
  Copy, 
  Check, 
  ChevronDown, 
  ChevronUp, 
  BookOpen, 
  Compass, 
  Code2, 
  Paintbrush, 
  Bot, 
  ExternalLink,
  MessageSquarePlus,
  Edit2
} from 'lucide-react';
import { useChatStore, ChatMessage } from '../stores/useChatStore';

const MODES = [
  { id: 'AUTO', label: 'Auto (Dynamic)', icon: Sparkles, color: 'text-nova-accent' },
  { id: 'QUICK', label: 'Quick Response', icon: Send, color: 'text-blue-400' },
  { id: 'THINK', label: 'Deep Think (Reasoning)', icon: BrainCircuit, color: 'text-purple-400' },
  { id: 'SEARCH', label: 'Grounded Search', icon: Search, color: 'text-nova-cyan' },
  { id: 'RESEARCH', label: 'Deep Research', icon: Compass, color: 'text-indigo-400' },
  { id: 'CODE', label: 'Code Assistant', icon: Code2, color: 'text-emerald-400' },
  { id: 'LEARN', label: 'Learning OS Tutor', icon: BookOpen, color: 'text-amber-400' },
  { id: 'CREATE', label: 'Studio Creator', icon: Paintbrush, color: 'text-rose-400' },
  { id: 'AGENT', label: 'Autonomous Agent', icon: Bot, color: 'text-teal-400' },
];

export const Chat: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const {
    conversations,
    activeConversationId,
    messages,
    selectedMode,
    isStreaming,
    streamingThought,
    streamingContent,
    setSelectedMode,
    fetchConversations,
    selectConversation,
    createNewConversation,
    sendMessage,
    stopStreaming,
    pinConversation,
    deleteConversation,
    branchConversation,
  } = useChatStore();

  const [input, setInput] = useState('');
  const [showModeDropdown, setShowModeDropdown] = useState(false);
  const [showThought, setShowThought] = useState(true);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchConversations();
  }, [fetchConversations]);

  useEffect(() => {
    if (id && id !== activeConversationId) {
      selectConversation(id);
    }
  }, [id, activeConversationId, selectConversation]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isStreaming) return;
    const text = input;
    setInput('');
    await sendMessage(text, true);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleCopy = (text: string, msgId: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(msgId);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleBranch = async (msgId: string) => {
    if (!activeConversationId) return;
    const newId = await branchConversation(activeConversationId, msgId);
    if (newId) {
      navigate(`/chat/${newId}`);
    }
  };

  const activeModeObj = MODES.find((m) => m.id === selectedMode) || MODES[0];
  const ActiveModeIcon = activeModeObj.icon;

  return (
    <div className="flex h-[calc(100vh-3.5rem)] overflow-hidden font-sans">
      {/* Left Chat History Pane */}
      <div className="w-64 border-r border-nova-800 bg-nova-900/50 flex flex-col justify-between shrink-0">
        <div className="p-3 border-b border-nova-800/80 flex items-center justify-between">
          <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">Conversations</span>
          <button
            onClick={() => createNewConversation()}
            className="p-1.5 text-nova-accent hover:bg-nova-850 rounded-lg transition-colors"
            title="New Chat"
          >
            <MessageSquarePlus className="h-4 w-4" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {conversations.length === 0 ? (
            <div className="text-center py-8 text-xs text-slate-500">No active threads</div>
          ) : (
            conversations.map((c) => (
              <div
                key={c.id}
                onClick={() => {
                  navigate(`/chat/${c.id}`);
                  selectConversation(c.id);
                }}
                className={`group flex items-center justify-between px-2.5 py-2 rounded-xl text-xs cursor-pointer transition-colors ${
                  activeConversationId === c.id
                    ? 'bg-nova-800 text-white font-semibold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-nova-850/60'
                }`}
              >
                <div className="flex items-center gap-2 truncate min-w-0">
                  {c.pinned && <Pin className="h-3 w-3 text-amber-400 shrink-0 rotate-45" />}
                  <span className="truncate">{c.title}</span>
                </div>
                <div className="hidden group-hover:flex items-center gap-1 shrink-0">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      pinConversation(c.id, !c.pinned);
                    }}
                    className="p-1 hover:text-amber-400 text-slate-500"
                    title={c.pinned ? 'Unpin' : 'Pin'}
                  >
                    <Pin className="h-3 w-3" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteConversation(c.id);
                    }}
                    className="p-1 hover:text-rose-400 text-slate-500"
                    title="Delete"
                  >
                    <Trash2 className="h-3 w-3" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main Conversation Pane */}
      <div className="flex-1 flex flex-col min-w-0 bg-nova-950">
        {/* Messages Thread */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 max-w-4xl mx-auto w-full">
          {messages.length === 0 && !isStreaming ? (
            <div className="flex flex-col items-center justify-center h-full text-center space-y-4 py-16">
              <div className="h-12 w-12 rounded-2xl bg-gradient-to-tr from-nova-accent to-nova-cyan flex items-center justify-center shadow-glow-md">
                <Sparkles className="h-6 w-6 text-white" />
              </div>
              <div className="space-y-1">
                <h3 className="text-xl font-bold text-white tracking-wide">NOVA X Universal Intelligence</h3>
                <p className="text-xs text-slate-400 max-w-md">
                  Ask questions, research topics, write code, run dev servers, or execute automated workflows.
                </p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg w-full pt-4">
                <button
                  onClick={() => sendMessage('Research state of the art hybrid RAG architectures', true)}
                  className="p-3 text-left rounded-xl bg-nova-900 border border-nova-800 hover:border-nova-accent/40 text-xs text-slate-300 hover:text-white transition-colors"
                >
                  🔍 Research state-of-the-art hybrid RAG
                </button>
                <button
                  onClick={() => sendMessage('Build a React expense tracker with TypeScript', true)}
                  className="p-3 text-left rounded-xl bg-nova-900 border border-nova-800 hover:border-nova-accent/40 text-xs text-slate-300 hover:text-white transition-colors"
                >
                  ⚡ Build a React expense tracker
                </button>
              </div>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-3.5 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.role === 'assistant' && (
                  <div className="h-8 w-8 rounded-xl bg-gradient-to-tr from-nova-accent to-nova-cyan flex items-center justify-center shrink-0 shadow-glow-sm mt-1">
                    <Sparkles className="h-4 w-4 text-white" />
                  </div>
                )}

                <div className={`space-y-2 max-w-2xl ${msg.role === 'user' ? 'w-auto' : 'flex-1'}`}>
                  {/* Thought Process Box */}
                  {msg.thought_process && (
                    <div className="rounded-xl border border-nova-800 bg-nova-900/60 overflow-hidden text-xs">
                      <button
                        onClick={() => setShowThought(!showThought)}
                        className="w-full px-3 py-1.5 flex items-center justify-between text-slate-400 hover:text-slate-200 bg-nova-850/50"
                      >
                        <div className="flex items-center gap-2">
                          <BrainCircuit className="h-3.5 w-3.5 text-purple-400" />
                          <span className="font-mono text-[11px]">Reasoning Chain</span>
                        </div>
                        {showThought ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
                      </button>
                      {showThought && (
                        <div className="p-3 text-slate-300 text-xs leading-relaxed font-mono bg-nova-950/40">
                          {msg.thought_process}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Main Bubble */}
                  <div
                    className={`p-4 rounded-2xl text-xs leading-relaxed ${
                      msg.role === 'user'
                        ? 'bg-gradient-to-r from-nova-accent to-blue-600 text-white rounded-tr-none shadow-glow-sm'
                        : 'glass-panel-elevated text-slate-200 rounded-tl-none border border-nova-800'
                    }`}
                  >
                    <div className="whitespace-pre-wrap">{msg.content}</div>

                    {/* Citations list if present */}
                    {msg.citations && msg.citations.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-nova-800/80 space-y-1.5">
                        <div className="text-[10px] uppercase font-mono tracking-wider text-slate-400 flex items-center gap-1.5">
                          <Search className="h-3 w-3 text-nova-cyan" />
                          <span>Grounded Citations</span>
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          {msg.citations.map((c, i) => (
                            <div
                              key={c.id || i}
                              className="p-2 rounded-lg bg-nova-900/80 border border-nova-800 text-[11px] space-y-1 hover:border-nova-accent/40 transition-colors"
                            >
                              <div className="font-bold text-slate-200 line-clamp-1">[{i + 1}] {c.title}</div>
                              <p className="text-slate-400 line-clamp-2 text-[10px]">{c.snippet}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Message actions */}
                  {msg.role === 'assistant' && (
                    <div className="flex items-center gap-2 text-slate-500 text-[11px] px-1">
                      <button
                        onClick={() => handleCopy(msg.content, msg.id)}
                        className="hover:text-slate-300 flex items-center gap-1"
                      >
                        {copiedId === msg.id ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
                        <span>{copiedId === msg.id ? 'Copied' : 'Copy'}</span>
                      </button>
                      <button
                        onClick={() => handleBranch(msg.id)}
                        className="hover:text-slate-300 flex items-center gap-1"
                      >
                        <GitBranch className="h-3 w-3" />
                        <span>Branch</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}

          {/* Real-time Streaming Message */}
          {isStreaming && (
            <div className="flex gap-3.5 justify-start">
              <div className="h-8 w-8 rounded-xl bg-gradient-to-tr from-nova-accent to-nova-cyan flex items-center justify-center shrink-0 shadow-glow-sm mt-1">
                <Sparkles className="h-4 w-4 text-white animate-pulse" />
              </div>
              <div className="space-y-2 flex-1 max-w-2xl">
                {streamingThought && (
                  <div className="p-3 rounded-xl border border-nova-800 bg-nova-900/60 text-xs font-mono text-purple-300 flex items-center gap-2">
                    <BrainCircuit className="h-4 w-4 animate-spin text-purple-400" />
                    <span>{streamingThought}</span>
                  </div>
                )}
                <div className="glass-panel-elevated p-4 rounded-2xl rounded-tl-none border border-nova-800 text-xs text-slate-200 leading-relaxed whitespace-pre-wrap">
                  {streamingContent || 'Thinking...'}
                  <span className="inline-block h-3 w-1.5 ml-1 bg-nova-accent animate-pulse" />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Composer Input Area (Part 14) */}
        <div className="p-4 border-t border-nova-800/80 max-w-4xl mx-auto w-full">
          <div className="glass-panel-elevated p-3 rounded-2xl border border-nova-750 shadow-2xl space-y-2">
            {/* Mode Tag & Dropdown */}
            <div className="flex items-center justify-between pb-1 border-b border-nova-800/60 relative">
              <div className="relative">
                <button
                  onClick={() => setShowModeDropdown(!showModeDropdown)}
                  className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-nova-900 border border-nova-800 hover:border-nova-700 text-xs text-slate-200 transition-colors"
                >
                  <ActiveModeIcon className={`h-3.5 w-3.5 ${activeModeObj.color}`} />
                  <span className="font-semibold">{activeModeObj.label}</span>
                  <ChevronDown className="h-3 w-3 text-slate-500" />
                </button>

                {showModeDropdown && (
                  <div className="absolute left-0 bottom-full mb-2 w-64 bg-nova-900 border border-nova-700 rounded-xl shadow-2xl p-1.5 z-30 space-y-0.5">
                    {MODES.map((m) => {
                      const Icon = m.icon;
                      return (
                        <button
                          key={m.id}
                          onClick={() => {
                            setSelectedMode(m.id);
                            setShowModeDropdown(false);
                          }}
                          className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg text-left text-xs transition-colors ${
                            selectedMode === m.id
                              ? 'bg-nova-accent/20 text-white font-semibold'
                              : 'text-slate-400 hover:text-slate-200 hover:bg-nova-850'
                          }`}
                        >
                          <Icon className={`h-4 w-4 ${m.color}`} />
                          <span>{m.label}</span>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>

              <span className="text-[10px] text-slate-500 font-mono">Shift + Enter for new line</span>
            </div>

            {/* Input Textarea */}
            <textarea
              rows={2}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={`Ask NOVA anything in ${activeModeObj.label} mode...`}
              className="w-full bg-transparent text-xs text-slate-100 placeholder-slate-500 focus:outline-none resize-none px-1"
            />

            {/* Controls Bar */}
            <div className="flex items-center justify-between pt-1">
              <div className="flex items-center gap-1">
                <button
                  type="button"
                  title="Attach file"
                  className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-nova-850 rounded-lg transition-colors"
                >
                  <Paperclip className="h-4 w-4" />
                </button>
                <button
                  type="button"
                  onClick={() => setSelectedMode(selectedMode === 'SEARCH' ? 'AUTO' : 'SEARCH')}
                  title="Web Search Grounding"
                  className={`p-1.5 rounded-lg transition-colors ${
                    selectedMode === 'SEARCH' ? 'bg-nova-cyan/20 text-nova-cyan' : 'text-slate-400 hover:text-slate-200 hover:bg-nova-850'
                  }`}
                >
                  <Search className="h-4 w-4" />
                </button>
                <button
                  type="button"
                  onClick={() => setSelectedMode(selectedMode === 'THINK' ? 'AUTO' : 'THINK')}
                  title="Deep Thinking Mode"
                  className={`p-1.5 rounded-lg transition-colors ${
                    selectedMode === 'THINK' ? 'bg-purple-500/20 text-purple-400' : 'text-slate-400 hover:text-slate-200 hover:bg-nova-850'
                  }`}
                >
                  <BrainCircuit className="h-4 w-4" />
                </button>
                <button
                  type="button"
                  title="Voice Input"
                  className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-nova-850 rounded-lg transition-colors"
                >
                  <Mic className="h-4 w-4" />
                </button>
              </div>

              {isStreaming ? (
                <button
                  type="button"
                  onClick={stopStreaming}
                  className="px-3.5 py-1.5 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 text-rose-400 font-semibold text-xs flex items-center gap-1.5 border border-rose-500/30"
                >
                  <Square className="h-3 w-3 fill-rose-400" />
                  <span>Stop</span>
                </button>
              ) : (
                <button
                  type="button"
                  onClick={() => handleSend()}
                  disabled={!input.trim()}
                  className="px-4 py-1.5 rounded-xl bg-gradient-to-r from-nova-accent to-blue-600 hover:from-blue-600 hover:to-nova-accent text-white font-semibold text-xs flex items-center gap-1.5 shadow-glow-sm disabled:opacity-40 transition-all active:scale-95"
                >
                  <span>Send</span>
                  <Send className="h-3 w-3" />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
