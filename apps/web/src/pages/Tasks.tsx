import React from 'react';
import { CheckSquare, Plus, Calendar, Clock } from 'lucide-react';

export const Tasks: React.FC = () => {
  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <CheckSquare className="h-5 w-5 text-emerald-400" />
            <span>Tasks & Reminders</span>
          </h1>
          <p className="text-xs text-slate-400">Contextual task management with project links and recurring notifications.</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs shadow-glow-sm">
          <Plus className="h-4 w-4" />
          <span>New Task</span>
        </button>
      </div>

      <div className="space-y-3">
        <div className="p-3.5 rounded-xl glass-panel flex items-center justify-between border border-nova-800">
          <div className="flex items-center gap-3">
            <input type="checkbox" defaultChecked className="rounded border-nova-700 text-nova-accent focus:ring-0" />
            <div>
              <span className="text-xs font-semibold text-slate-200 line-through text-slate-400">Phase 0: Scaffold monorepo and verify health endpoint</span>
              <div className="text-[10px] text-slate-500 font-mono">Architecture Foundation</div>
            </div>
          </div>
          <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">DONE</span>
        </div>

        <div className="p-3.5 rounded-xl glass-panel flex items-center justify-between border border-nova-800">
          <div className="flex items-center gap-3">
            <input type="checkbox" defaultChecked className="rounded border-nova-700 text-nova-accent focus:ring-0" />
            <div>
              <span className="text-xs font-semibold text-slate-200">Phase 1: Build JWT Auth and Full Application Shell</span>
              <div className="text-[10px] text-slate-500 font-mono">FastAPI + React 19 Shell</div>
            </div>
          </div>
          <span className="text-[10px] font-mono text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded">VERIFIED</span>
        </div>

        <div className="p-3.5 rounded-xl glass-panel flex items-center justify-between border border-nova-800">
          <div className="flex items-center gap-3">
            <input type="checkbox" className="rounded border-nova-700 text-nova-accent focus:ring-0" />
            <div>
              <span className="text-xs font-semibold text-slate-200">Phase 2: Universal Chat with Streaming & Branching</span>
              <div className="text-[10px] text-slate-500 font-mono">SSE Tokens & Citations</div>
            </div>
          </div>
          <span className="text-[10px] font-mono text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded">UP NEXT</span>
        </div>
      </div>
    </div>
  );
};
