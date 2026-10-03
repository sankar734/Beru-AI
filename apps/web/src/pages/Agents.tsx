import React from 'react';
import { Bot, Play, Pause, AlertTriangle, ShieldCheck, CheckCircle2 } from 'lucide-react';

export const Agents: React.FC = () => {
  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Bot className="h-5 w-5 text-blue-400" />
            <span>Autonomous Goal Execution Agents</span>
          </h1>
          <p className="text-xs text-slate-400">Step-by-step goal execution with policy barriers and human confirmation gates.</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs shadow-glow-sm">
          <span>Start New Agent</span>
        </button>
      </div>

      <div className="glass-panel p-6 rounded-2xl space-y-4 border border-nova-750">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <div className="text-xs font-mono text-nova-cyan">Active Agent Run #AG-4091</div>
            <h3 className="text-sm font-bold text-white">Audit codebase security and build verification</h3>
          </div>
          <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
            STEP 3 OF 5
          </span>
        </div>

        {/* Step Progression (Part 47) */}
        <div className="space-y-2 pt-2">
          <div className="flex items-center gap-3 p-2 rounded-lg bg-nova-900/60 text-xs text-slate-300">
            <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
            <span>1. Scan project directories and manifests</span>
            <span className="text-[10px] text-slate-500 ml-auto font-mono">COMPLETED</span>
          </div>
          <div className="flex items-center gap-3 p-2 rounded-lg bg-nova-900/60 text-xs text-slate-300">
            <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
            <span>2. Run dependency vulnerability check</span>
            <span className="text-[10px] text-slate-500 ml-auto font-mono">COMPLETED</span>
          </div>
          <div className="flex items-center gap-3 p-2 rounded-lg bg-nova-850 border border-nova-accent/30 text-xs text-white">
            <span className="h-2 w-2 rounded-full bg-nova-accent animate-pulse shrink-0" />
            <span>3. Compile React client and run typechecks</span>
            <span className="text-[10px] text-nova-accent ml-auto font-mono">RUNNING</span>
          </div>
          <div className="flex items-center gap-3 p-2 rounded-lg bg-nova-900/40 text-xs text-slate-500">
            <span className="h-2 w-2 rounded-full bg-slate-700 shrink-0" />
            <span>4. Run unit and integration test suites</span>
            <span className="text-[10px] text-slate-600 ml-auto font-mono">PENDING</span>
          </div>
          <div className="flex items-center gap-3 p-2 rounded-lg bg-nova-900/40 text-xs text-slate-500">
            <span className="h-2 w-2 rounded-full bg-slate-700 shrink-0" />
            <span>5. Generate verification audit report</span>
            <span className="text-[10px] text-slate-600 ml-auto font-mono">PENDING</span>
          </div>
        </div>

        <div className="flex items-center justify-between pt-2 border-t border-nova-800">
          <span className="text-[11px] text-slate-500">Hard limit: Max 15 steps • 300s timeout</span>
          <div className="flex items-center gap-2">
            <button className="px-3 py-1.5 rounded-lg bg-nova-850 hover:bg-nova-800 text-xs text-slate-300">
              Pause
            </button>
            <button className="px-3 py-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-xs text-rose-400 border border-rose-500/30">
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
