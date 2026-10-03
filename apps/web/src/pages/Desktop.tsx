import React from 'react';
import { Laptop, ShieldCheck, Folder, Power, RefreshCw, AlertTriangle, Terminal, CheckCircle2 } from 'lucide-react';

export const Desktop: React.FC = () => {
  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      {/* Top Banner (Part 126) */}
      <div className="glass-panel p-6 rounded-2xl border border-nova-750 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="h-12 w-12 rounded-2xl bg-nova-cyan/15 border border-nova-cyan/30 flex items-center justify-center text-nova-cyan shadow-glow-cyan">
            <Laptop className="h-6 w-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-white">DESKTOP-5CJ3QI6</h2>
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                CONNECTED
              </span>
            </div>
            <p className="text-xs text-slate-400">Windows 11 • Companion Daemon on 127.0.0.1:9000 (Loopback only)</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-nova-850 hover:bg-nova-800 text-xs text-slate-300">
            <RefreshCw className="h-3.5 w-3.5" />
            <span>Rescan</span>
          </button>
          <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-xs text-rose-400 font-semibold">
            <Power className="h-3.5 w-3.5" />
            <span>Emergency Stop</span>
          </button>
        </div>
      </div>

      {/* Allowed Folders & Capabilities (Part 90, 91) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-panel p-6 rounded-2xl space-y-4 border border-nova-750">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <Folder className="h-4 w-4 text-nova-accent" />
              <span>Approved Directory Allowlists</span>
            </h3>
            <span className="text-[10px] text-nova-emerald font-mono">STRICT ACCESS</span>
          </div>

          <div className="space-y-2">
            <div className="p-3 rounded-xl bg-nova-900/80 border border-nova-800 flex items-center justify-between text-xs font-mono">
              <span className="text-slate-200">D:\5536\Projects\Beru</span>
              <span className="text-emerald-400 text-[10px]">READ / WRITE</span>
            </div>
            <div className="p-3 rounded-xl bg-nova-900/80 border border-nova-800 flex items-center justify-between text-xs font-mono">
              <span className="text-slate-200">D:\5536\Projects\EventSphere</span>
              <span className="text-emerald-400 text-[10px]">READ / WRITE</span>
            </div>
          </div>
          <p className="text-[11px] text-slate-500">NOVA cannot read or mutate any path outside approved root directories.</p>
        </div>

        <div className="glass-panel p-6 rounded-2xl space-y-4 border border-nova-750">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-nova-cyan" />
              <span>Desktop Permission Center</span>
            </h3>
            <span className="text-[10px] text-slate-500 font-mono">ZERO PRIVILEGE</span>
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex justify-between items-center p-2 rounded-lg bg-nova-900/60">
              <span className="text-slate-300">Application Launching</span>
              <span className="text-nova-accent font-semibold">ALLOW SAFE (VS Code, Chrome, Calc)</span>
            </div>
            <div className="flex justify-between items-center p-2 rounded-lg bg-nova-900/60">
              <span className="text-slate-300">File Deletion (Level 4)</span>
              <span className="text-rose-400 font-semibold">ALWAYS ASK CONFIRMATION</span>
            </div>
            <div className="flex justify-between items-center p-2 rounded-lg bg-nova-900/60">
              <span className="text-slate-300">Screen Capture</span>
              <span className="text-amber-400 font-semibold">ON DEMAND (Active Window Only)</span>
            </div>
            <div className="flex justify-between items-center p-2 rounded-lg bg-nova-900/60">
              <span className="text-slate-300">Arbitrary Shell Access</span>
              <span className="text-rose-400 font-semibold">BLOCKED / FORBIDDEN</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
