import React from 'react';
import { FolderKanban, Plus, FileText, Code2, CheckCircle2 } from 'lucide-react';

export const Projects: React.FC = () => {
  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <FolderKanban className="h-5 w-5 text-purple-400" />
            <span>Projects & Context Spaces</span>
          </h1>
          <p className="text-xs text-slate-400">Isolated workspace scopes with custom instructions, files, and artifacts.</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs shadow-glow-sm">
          <Plus className="h-4 w-4" />
          <span>New Project</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div className="glass-panel p-5 rounded-2xl space-y-3 border border-nova-750">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white">NOVA X Intelligence OS</h3>
            <span className="text-[10px] font-mono text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">Active</span>
          </div>
          <p className="text-xs text-slate-400">Complete multi-phase AI platform architecture with desktop companion integration.</p>
          <div className="flex items-center gap-4 text-[11px] text-slate-500 pt-2 border-t border-nova-800">
            <span>29 Files</span>
            <span>4 Artifacts</span>
            <span>7 Tasks</span>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl space-y-3 border border-nova-750">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white">EventSphere App</h3>
            <span className="text-[10px] font-mono text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/20">Development</span>
          </div>
          <p className="text-xs text-slate-400">Event ticketing and booking system with React frontend and FastAPI microservices.</p>
          <div className="flex items-center gap-4 text-[11px] text-slate-500 pt-2 border-t border-nova-800">
            <span>42 Files</span>
            <span>2 Artifacts</span>
            <span>3 Tasks</span>
          </div>
        </div>
      </div>
    </div>
  );
};
