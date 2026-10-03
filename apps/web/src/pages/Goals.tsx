import React from 'react';
import { Target, Flag, CheckCircle, TrendingUp } from 'lucide-react';

export const Goals: React.FC = () => {
  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <div className="space-y-1">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <Target className="h-5 w-5 text-purple-400" />
          <span>Goals & Autopilot System</span>
        </h1>
        <p className="text-xs text-slate-400">Autonomous pacing, milestone tracking, and daily structured curriculum guidance.</p>
      </div>

      <div className="glass-panel p-6 rounded-2xl space-y-4 border border-nova-750">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-white">Full Stack AI Systems Engineer (60-Day Sprint)</h3>
            <p className="text-xs text-slate-400">Autopilot guidance with daily practice, code reviews, and mock interviews.</p>
          </div>
          <span className="text-xs font-mono font-bold text-purple-400 bg-purple-500/10 px-3 py-1 rounded-full border border-purple-500/20">
            DAY 18 OF 60 • 30% PROGRESS
          </span>
        </div>

        <div className="w-full bg-nova-900 rounded-full h-2.5 overflow-hidden border border-nova-800">
          <div className="bg-gradient-to-r from-purple-500 to-blue-500 h-full w-[30%] rounded-full" />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
          <div className="p-3 rounded-xl bg-nova-900/60 border border-nova-800 text-xs">
            <span className="text-slate-500 block text-[10px] font-mono">MILESTONE 1</span>
            <span className="font-semibold text-slate-200">AsyncIO & API Microservices</span>
            <span className="text-emerald-400 block text-[10px] font-mono mt-1">✓ COMPLETED</span>
          </div>
          <div className="p-3 rounded-xl bg-nova-850 border border-purple-500/30 text-xs">
            <span className="text-purple-400 block text-[10px] font-mono">MILESTONE 2 (CURRENT)</span>
            <span className="font-semibold text-white">Hybrid RAG & Cross-Encoders</span>
            <span className="text-purple-400 block text-[10px] font-mono mt-1">● IN PROGRESS</span>
          </div>
          <div className="p-3 rounded-xl bg-nova-900/40 border border-nova-800 text-xs text-slate-500">
            <span className="text-slate-600 block text-[10px] font-mono">MILESTONE 3</span>
            <span className="font-medium text-slate-400">OS Automation & Win32 APIs</span>
            <span className="text-slate-600 block text-[10px] font-mono mt-1">UPCOMING</span>
          </div>
        </div>
      </div>
    </div>
  );
};
