import React from 'react';
import { Workflow as WorkflowIcon, Plus, Play, GitBranch } from 'lucide-react';

export const Workflows: React.FC = () => {
  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <WorkflowIcon className="h-5 w-5 text-purple-400" />
            <span>Visual Workflow Automation</span>
          </h1>
          <p className="text-xs text-slate-400">Trigger-driven DAG pipelines connecting AI reasoning, web research, code execution, and desktop actions.</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs shadow-glow-sm">
          <Plus className="h-4 w-4" />
          <span>New Workflow</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div className="glass-panel p-5 rounded-2xl space-y-3 border border-nova-750">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white">Daily Tech Intelligence Briefing</h3>
            <button className="p-1.5 rounded-lg bg-nova-850 hover:bg-nova-800 text-nova-accent">
              <Play className="h-3.5 w-3.5" />
            </button>
          </div>
          <p className="text-xs text-slate-400">Cron Trigger (09:00 AM) → SearXNG AI Search → Summarizer → Save to Studio Document.</p>
          <div className="text-[10px] text-slate-500 font-mono">4 Nodes • Last run 10 hours ago (Success)</div>
        </div>

        <div className="glass-panel p-5 rounded-2xl space-y-3 border border-nova-750">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white">Automated Code Health Check</h3>
            <button className="p-1.5 rounded-lg bg-nova-850 hover:bg-nova-800 text-nova-accent">
              <Play className="h-3.5 w-3.5" />
            </button>
          </div>
          <p className="text-xs text-slate-400">Git Commit Trigger → Run pytest in Sandbox → If errors, generate repair diff and notify user.</p>
          <div className="text-[10px] text-slate-500 font-mono">5 Nodes • Active Watcher</div>
        </div>
      </div>
    </div>
  );
};
