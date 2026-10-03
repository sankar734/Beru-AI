import React from 'react';
import { Settings as SettingsIcon, Shield, Sliders, Key, HardDrive, Bell } from 'lucide-react';
import { useAuthStore } from '../stores/useAuthStore';

export const Settings: React.FC = () => {
  const { user } = useAuthStore();

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-6">
      <div className="space-y-1">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <SettingsIcon className="h-5 w-5 text-slate-400" />
          <span>System Settings & Preferences</span>
        </h1>
        <p className="text-xs text-slate-400">Configure model providers, privacy boundaries, desktop access, and notifications.</p>
      </div>

      <div className="space-y-4">
        {/* User Profile */}
        <div className="glass-panel p-6 rounded-2xl space-y-3 border border-nova-750">
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300">Operator Profile</h3>
          <div className="grid grid-cols-2 gap-4 text-xs">
            <div>
              <span className="text-slate-500 block">Name</span>
              <span className="text-white font-semibold">{user?.name || 'Nova Operator'}</span>
            </div>
            <div>
              <span className="text-slate-500 block">Email</span>
              <span className="text-white font-semibold">{user?.email || 'operator@novax.local'}</span>
            </div>
          </div>
        </div>

        {/* AI Model Preferences */}
        <div className="glass-panel p-6 rounded-2xl space-y-4 border border-nova-750">
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <Sliders className="h-4 w-4 text-nova-accent" />
            <span>AI Model & Provider Routing</span>
          </h3>

          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-3 rounded-xl bg-nova-900/60 border border-nova-800">
              <div>
                <div className="font-semibold text-white">Default Model Routing</div>
                <div className="text-[11px] text-slate-400">Auto-routes between quick, reasoning, and vision pipelines</div>
              </div>
              <span className="font-mono text-nova-accent bg-nova-accent/10 px-2.5 py-1 rounded">AUTO DYNAMIC</span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-nova-900/60 border border-nova-800">
              <div>
                <div className="font-semibold text-white">Local-Only AI Fallback</div>
                <div className="text-[11px] text-slate-400">Enforce zero-cloud transmission for sensitive desktop files</div>
              </div>
              <input type="checkbox" className="rounded border-nova-700 text-nova-accent" />
            </div>
          </div>
        </div>

        {/* Security & Memory Policy */}
        <div className="glass-panel p-6 rounded-2xl space-y-4 border border-nova-750">
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <Shield className="h-4 w-4 text-nova-emerald" />
            <span>Memory & Privacy Policy (Part 31, 32)</span>
          </h3>

          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-3 rounded-xl bg-nova-900/60 border border-nova-800">
              <div>
                <div className="font-semibold text-white">Long-Term Memory Retention</div>
                <div className="text-[11px] text-slate-400">Allows NOVA to remember preferences and recurring workflows</div>
              </div>
              <input type="checkbox" defaultChecked className="rounded border-nova-700 text-nova-accent" />
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-nova-900/60 border border-nova-800">
              <div>
                <div className="font-semibold text-white">Consequential Action Barriers</div>
                <div className="text-[11px] text-slate-400">Always require confirmation for Level 3 and 4 actions</div>
              </div>
              <span className="font-mono text-nova-emerald bg-emerald-500/10 px-2.5 py-1 rounded">ENFORCED</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
