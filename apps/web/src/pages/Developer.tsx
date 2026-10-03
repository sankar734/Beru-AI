import React from 'react';
import { Terminal, Play, Square, RefreshCw, GitBranch, AlertCircle, CheckCircle2 } from 'lucide-react';

export const Developer: React.FC = () => {
  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Terminal className="h-5 w-5 text-nova-emerald" />
            <span>Developer Mode & Service Supervisor</span>
          </h1>
          <p className="text-xs text-slate-400">Controlled execution of approved dev servers, build pipelines, and error root-cause diagnosis.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="glass-panel p-5 rounded-2xl space-y-3 border border-nova-750">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-white">Frontend Dev Server</span>
            <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">ONLINE</span>
          </div>
          <p className="text-xs text-slate-400">Vite React client running on port 5173</p>
          <div className="flex items-center gap-2 pt-2">
            <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/30 text-xs">
              <Square className="h-3 w-3" />
              <span>Stop</span>
            </button>
            <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-nova-850 text-slate-300 text-xs">
              <RefreshCw className="h-3 w-3" />
              <span>Restart</span>
            </button>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl space-y-3 border border-nova-750">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-white">Backend API Server</span>
            <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">ONLINE</span>
          </div>
          <p className="text-xs text-slate-400">FastAPI Uvicorn running on port 8000</p>
          <div className="flex items-center gap-2 pt-2">
            <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/30 text-xs">
              <Square className="h-3 w-3" />
              <span>Stop</span>
            </button>
            <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-nova-850 text-slate-300 text-xs">
              <RefreshCw className="h-3 w-3" />
              <span>Restart</span>
            </button>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl space-y-3 border border-nova-750">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-white">Git Health Status</span>
            <span className="text-[10px] font-mono text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded">CLEAN</span>
          </div>
          <p className="text-xs text-slate-400">Branch: master • 0 uncommitted changes</p>
          <div className="flex items-center gap-2 pt-2 text-xs text-slate-400">
            <GitBranch className="h-3.5 w-3.5" />
            <span>HEAD: Phase 0 verified</span>
          </div>
        </div>
      </div>

      {/* Live Log Stream Simulation */}
      <div className="glass-panel p-4 rounded-2xl space-y-2 border border-nova-800 font-mono text-xs">
        <div className="flex items-center justify-between text-slate-400 pb-2 border-b border-nova-800">
          <span>Supervised Process Output (Vite + Uvicorn)</span>
          <span className="text-[10px] text-emerald-400">● STREAMING</span>
        </div>
        <div className="text-slate-300">INFO:     127.0.0.1:5173 - GET /api/v1/health HTTP/1.1 200 OK</div>
        <div className="text-emerald-400">[Vite] Ready in 218ms at http://localhost:5173/</div>
        <div className="text-slate-400">INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)</div>
      </div>
    </div>
  );
};
