import React from 'react';
import { Compass, Sparkles, Layers, CheckCircle2, Clock } from 'lucide-react';

export const Research: React.FC = () => {
  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <div className="space-y-1">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <Compass className="h-5 w-5 text-blue-400" />
          <span>Deep Research System</span>
        </h1>
        <p className="text-xs text-slate-400">Autonomous multi-agent research jobs synthesizing exhaustive, fact-checked reports.</p>
      </div>

      <div className="glass-panel p-6 rounded-2xl space-y-4 border border-nova-750">
        <label className="text-xs font-semibold text-slate-300">Research Objective or Thesis</label>
        <textarea
          rows={3}
          placeholder="e.g., Investigate state-of-the-art hybrid RAG architectures with cross-encoder reranking and compare performance against pure vector retrieval..."
          className="w-full bg-nova-900 border border-nova-800 rounded-xl p-3 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-400 resize-none"
        />
        <div className="flex justify-between items-center">
          <span className="text-[11px] text-slate-500">Autonomous pipeline: Planning → Parallel Search → Evidence Extraction → Verification → Synthesis</span>
          <button className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-semibold text-xs shadow-glow-sm">
            Launch Deep Research
          </button>
        </div>
      </div>
    </div>
  );
};
