import React from 'react';
import { Search as SearchIcon, Globe, Newspaper, GraduationCap, FileCode2, ArrowRight } from 'lucide-react';

export const Search: React.FC = () => {
  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <div className="space-y-1">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <SearchIcon className="h-5 w-5 text-nova-cyan" />
          <span>Grounded AI Search</span>
        </h1>
        <p className="text-xs text-slate-400">Search the live web with verified source citations and zero hallucinations.</p>
      </div>

      <div className="glass-panel p-4 rounded-2xl flex items-center gap-3 border border-nova-750">
        <SearchIcon className="h-5 w-5 text-nova-cyan shrink-0" />
        <input 
          type="text" 
          placeholder="Search web, news, academic papers, and developer docs..." 
          className="w-full bg-transparent text-sm text-slate-100 placeholder-slate-500 focus:outline-none"
        />
        <button className="px-4 py-2 bg-nova-accent hover:bg-blue-600 text-white font-semibold text-xs rounded-xl shadow-glow-sm">
          Search
        </button>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <button className="p-3 rounded-xl bg-nova-900 border border-nova-800 text-left hover:border-nova-cyan/40">
          <Globe className="h-4 w-4 text-nova-cyan mb-2" />
          <div className="text-xs font-semibold text-white">Web Mode</div>
          <div className="text-[10px] text-slate-500">Live web indexing</div>
        </button>
        <button className="p-3 rounded-xl bg-nova-900 border border-nova-800 text-left hover:border-blue-400/40">
          <Newspaper className="h-4 w-4 text-blue-400 mb-2" />
          <div className="text-xs font-semibold text-white">News Mode</div>
          <div className="text-[10px] text-slate-500">Real-time headlines</div>
        </button>
        <button className="p-3 rounded-xl bg-nova-900 border border-nova-800 text-left hover:border-purple-400/40">
          <GraduationCap className="h-4 w-4 text-purple-400 mb-2" />
          <div className="text-xs font-semibold text-white">Academic Mode</div>
          <div className="text-[10px] text-slate-500">Peer-reviewed papers</div>
        </button>
        <button className="p-3 rounded-xl bg-nova-900 border border-nova-800 text-left hover:border-emerald-400/40">
          <FileCode2 className="h-4 w-4 text-emerald-400 mb-2" />
          <div className="text-xs font-semibold text-white">Docs Mode</div>
          <div className="text-[10px] text-slate-500">Official API & SDK docs</div>
        </button>
      </div>
    </div>
  );
};
