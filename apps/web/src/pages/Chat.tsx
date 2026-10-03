import React from 'react';
import { Sparkles, Send, Paperclip, Search, BrainCircuit, Mic } from 'lucide-react';

export const Chat: React.FC = () => {
  return (
    <div className="flex flex-col h-[calc(100vh-3.5rem)] max-w-5xl mx-auto p-6 justify-between animate-in fade-in duration-200">
      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto space-y-6 pr-2">
        {/* Welcome Message */}
        <div className="flex gap-4 p-5 rounded-2xl glass-panel border border-nova-800">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-nova-accent to-nova-cyan flex items-center justify-center shrink-0 shadow-glow-sm">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div className="space-y-2 flex-1">
            <div className="flex items-center justify-between">
              <span className="font-bold text-sm text-white">NOVA X Orchestrator</span>
              <span className="text-[11px] font-mono text-nova-cyan bg-nova-cyan/10 px-2 py-0.5 rounded border border-nova-cyan/20">
                AUTO MODE
              </span>
            </div>
            <p className="text-sm text-slate-300 leading-relaxed">
              Hello! I am NOVA X, your Personal Intelligence Operating System. You can ask me questions, initiate deep research, analyze codebases, create studio artifacts, or control your local developer services.
            </p>
            <div className="flex flex-wrap gap-2 pt-2">
              <button className="text-xs px-3 py-1.5 rounded-lg bg-nova-900 border border-nova-800 hover:border-nova-accent/40 text-slate-300 hover:text-white transition-colors">
                🔍 Research RAG Architecture
              </button>
              <button className="text-xs px-3 py-1.5 rounded-lg bg-nova-900 border border-nova-800 hover:border-nova-accent/40 text-slate-300 hover:text-white transition-colors">
                💻 Run React dev server
              </button>
              <button className="text-xs px-3 py-1.5 rounded-lg bg-nova-900 border border-nova-800 hover:border-nova-accent/40 text-slate-300 hover:text-white transition-colors">
                📚 Practice Python Algorithms
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Composer Input Bar (Part 14) */}
      <div className="pt-4">
        <div className="glass-panel-elevated p-3 rounded-2xl shadow-xl space-y-2 border border-nova-750">
          <textarea
            rows={2}
            placeholder="Ask NOVA anything... (Type / for modes, drag & drop files)"
            className="w-full bg-transparent text-sm text-slate-100 placeholder-slate-500 focus:outline-none resize-none px-2"
          />

          <div className="flex items-center justify-between pt-1 border-t border-nova-800/80">
            <div className="flex items-center gap-1.5">
              <button title="Attach file" className="p-2 text-slate-400 hover:text-slate-200 hover:bg-nova-800 rounded-lg transition-colors">
                <Paperclip className="h-4 w-4" />
              </button>
              <button title="Search Grounding" className="p-2 text-slate-400 hover:text-nova-cyan hover:bg-nova-800 rounded-lg transition-colors">
                <Search className="h-4 w-4" />
              </button>
              <button title="Deep Think" className="p-2 text-slate-400 hover:text-purple-400 hover:bg-nova-800 rounded-lg transition-colors">
                <BrainCircuit className="h-4 w-4" />
              </button>
              <button title="Voice Input" className="p-2 text-slate-400 hover:text-rose-400 hover:bg-nova-800 rounded-lg transition-colors">
                <Mic className="h-4 w-4" />
              </button>
            </div>

            <button className="h-8 px-4 rounded-xl bg-gradient-to-r from-nova-accent to-blue-600 hover:from-blue-600 hover:to-nova-accent text-white font-semibold text-xs flex items-center gap-2 shadow-glow-sm">
              <span>Send</span>
              <Send className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
