import React from 'react';
import { Paintbrush, FileText, Code2, Layout, Presentation, Plus } from 'lucide-react';

export const Studio: React.FC = () => {
  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Paintbrush className="h-5 w-5 text-purple-400" />
            <span>NOVA Studio</span>
          </h1>
          <p className="text-xs text-slate-400">Interactive workspace for documents, web apps, presentations, and diagrams.</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs shadow-glow-sm">
          <Plus className="h-4 w-4" />
          <span>New Artifact</span>
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-nova-900 border border-nova-800 hover:border-purple-400/40 cursor-pointer transition-colors space-y-2">
          <FileText className="h-5 w-5 text-purple-400" />
          <div className="text-xs font-bold text-white">Technical Architecture Doc</div>
          <div className="text-[11px] text-slate-400">Version 2 • 3 mins ago</div>
        </div>
        <div className="p-4 rounded-xl bg-nova-900 border border-nova-800 hover:border-blue-400/40 cursor-pointer transition-colors space-y-2">
          <Code2 className="h-5 w-5 text-blue-400" />
          <div className="text-xs font-bold text-white">Expense Tracker Web App</div>
          <div className="text-[11px] text-slate-400">Version 1 • 1 hour ago</div>
        </div>
        <div className="p-4 rounded-xl bg-nova-900 border border-nova-800 hover:border-emerald-400/40 cursor-pointer transition-colors space-y-2">
          <Presentation className="h-5 w-5 text-emerald-400" />
          <div className="text-xs font-bold text-white">AI Operating System Slides</div>
          <div className="text-[11px] text-slate-400">Version 1 • Yesterday</div>
        </div>
        <div className="p-4 rounded-xl bg-nova-900 border border-nova-800 hover:border-amber-400/40 cursor-pointer transition-colors space-y-2">
          <Layout className="h-5 w-5 text-amber-400" />
          <div className="text-xs font-bold text-white">Security Threat Model Diagram</div>
          <div className="text-[11px] text-slate-400">Version 4 • 2 days ago</div>
        </div>
      </div>
    </div>
  );
};
