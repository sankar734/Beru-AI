import React from 'react';
import { BrainCircuit, Plus, UserCheck, Shield } from 'lucide-react';

export const Experts: React.FC = () => {
  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <BrainCircuit className="h-5 w-5 text-purple-400" />
            <span>Custom AI Experts</span>
          </h1>
          <p className="text-xs text-slate-400">Specialized personas configured with bespoke system prompts, knowledge, and tools.</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs shadow-glow-sm">
          <Plus className="h-4 w-4" />
          <span>Create Expert</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="glass-panel p-5 rounded-2xl space-y-3 border border-nova-750">
          <div className="h-9 w-9 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400 font-bold">
            PT
          </div>
          <div className="text-xs font-bold text-white">Python Architect</div>
          <p className="text-[11px] text-slate-400">Specialized in AsyncIO, Pydantic, high-throughput microservices, and refactoring.</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl space-y-3 border border-nova-750">
          <div className="h-9 w-9 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 font-bold">
            RA
          </div>
          <div className="text-xs font-bold text-white">Research Analyst</div>
          <p className="text-[11px] text-slate-400">Fact checking, citation verification, peer-reviewed literature synthesis.</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl space-y-3 border border-nova-750">
          <div className="h-9 w-9 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 font-bold">
            IC
          </div>
          <div className="text-xs font-bold text-white">Interview Coach</div>
          <p className="text-[11px] text-slate-400">Technical coding rounds, system design challenges, and behavioral coaching.</p>
        </div>
      </div>
    </div>
  );
};
