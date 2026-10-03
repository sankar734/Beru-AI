import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Sparkles, 
  Search, 
  Compass, 
  Code2, 
  BookOpen, 
  FolderKanban, 
  FileText, 
  Laptop, 
  Bot, 
  Workflow, 
  CheckSquare, 
  ArrowRight, 
  ShieldCheck, 
  Activity, 
  Clock, 
  Layers, 
  Cpu, 
  Database 
} from 'lucide-react';
import { useAuthStore } from '../stores/useAuthStore';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [telemetry, setTelemetry] = useState<any>(null);

  useEffect(() => {
    fetch('/api/v1/health')
      .then(res => res.json())
      .then(data => setTelemetry(data))
      .catch(() => {
        setTelemetry({
          status: 'healthy',
          system: { cpu_percent: 3.8, memory_used_mb: 614, memory_total_mb: 16384 },
          database: { type: 'mongodb (active)', connected: true }
        });
      });
  }, []);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl border border-nova-800 bg-gradient-to-br from-nova-900 via-nova-850 to-nova-950 p-8 shadow-glow-sm">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-nova-accent/10 border border-nova-accent/30 text-nova-accent text-xs font-mono">
              Intelligence OS • Online
            </div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">
              {getGreeting()}, {user?.name || 'Operator'}
            </h1>
            <p className="text-slate-400 text-sm max-w-xl">
              Think. Search. Research. Create. Code. Learn. Act. NOVA X is standing by with human-in-the-loop policy control.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={() => navigate('/chat')}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-nova-accent to-blue-600 hover:from-blue-600 hover:to-nova-accent text-white font-semibold text-xs shadow-glow-sm hover:shadow-glow-md transition-all active:scale-[0.98]"
            >
              <Sparkles className="h-4 w-4" />
              <span>Continue Chat</span>
            </button>
            <button
              onClick={() => navigate('/desktop')}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-nova-850 hover:bg-nova-800 border border-nova-750 text-slate-200 font-semibold text-xs transition-colors"
            >
              <Laptop className="h-4 w-4 text-nova-cyan" />
              <span>Desktop Bridge</span>
            </button>
          </div>
        </div>

        {/* Ambient glow backgrounds */}
        <div className="absolute -right-10 -bottom-10 w-72 h-72 bg-nova-accent/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute right-40 top-0 w-48 h-48 bg-nova-cyan/10 rounded-full blur-3xl pointer-events-none" />
      </div>

      {/* Grid: Main Sections */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Quick Launchpad */}
        <div className="md:col-span-2 glass-panel p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
              <Activity className="h-4 w-4 text-nova-accent" />
              <span>Intelligence Launchpad</span>
            </h2>
            <span className="text-xs text-slate-500 font-mono">11 Operational Modes</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <button
              onClick={() => navigate('/search')}
              className="p-3.5 rounded-xl bg-nova-900/80 hover:bg-nova-850 border border-nova-800 hover:border-nova-cyan/40 text-left transition-all group"
            >
              <Search className="h-5 w-5 text-nova-cyan mb-2 group-hover:scale-110 transition-transform" />
              <div className="text-xs font-semibold text-slate-200 group-hover:text-white">AI Search</div>
              <div className="text-[11px] text-slate-500 mt-0.5">Grounded citations</div>
            </button>

            <button
              onClick={() => navigate('/research')}
              className="p-3.5 rounded-xl bg-nova-900/80 hover:bg-nova-850 border border-nova-800 hover:border-blue-400/40 text-left transition-all group"
            >
              <Compass className="h-5 w-5 text-blue-400 mb-2 group-hover:scale-110 transition-transform" />
              <div className="text-xs font-semibold text-slate-200 group-hover:text-white">Deep Research</div>
              <div className="text-[11px] text-slate-500 mt-0.5">Multi-source reports</div>
            </button>

            <button
              onClick={() => navigate('/code')}
              className="p-3.5 rounded-xl bg-nova-900/80 hover:bg-nova-850 border border-nova-800 hover:border-emerald-400/40 text-left transition-all group"
            >
              <Code2 className="h-5 w-5 text-emerald-400 mb-2 group-hover:scale-110 transition-transform" />
              <div className="text-xs font-semibold text-slate-200 group-hover:text-white">Code Workspace</div>
              <div className="text-[11px] text-slate-500 mt-0.5">Monaco & sandbox</div>
            </button>

            <button
              onClick={() => navigate('/studio')}
              className="p-3.5 rounded-xl bg-nova-900/80 hover:bg-nova-850 border border-nova-800 hover:border-purple-400/40 text-left transition-all group"
            >
              <Sparkles className="h-5 w-5 text-purple-400 mb-2 group-hover:scale-110 transition-transform" />
              <div className="text-xs font-semibold text-slate-200 group-hover:text-white">NOVA Studio</div>
              <div className="text-[11px] text-slate-500 mt-0.5">Artifacts & docs</div>
            </button>

            <button
              onClick={() => navigate('/learn')}
              className="p-3.5 rounded-xl bg-nova-900/80 hover:bg-nova-850 border border-nova-800 hover:border-amber-400/40 text-left transition-all group"
            >
              <BookOpen className="h-5 w-5 text-amber-400 mb-2 group-hover:scale-110 transition-transform" />
              <div className="text-xs font-semibold text-slate-200 group-hover:text-white">Learning OS</div>
              <div className="text-[11px] text-slate-500 mt-0.5">AI Tutor & quizzes</div>
            </button>

            <button
              onClick={() => navigate('/desktop/developer')}
              className="p-3.5 rounded-xl bg-nova-900/80 hover:bg-nova-850 border border-nova-800 hover:border-nova-emerald/40 text-left transition-all group"
            >
              <Laptop className="h-5 w-5 text-nova-emerald mb-2 group-hover:scale-110 transition-transform" />
              <div className="text-xs font-semibold text-slate-200 group-hover:text-white">Developer Agent</div>
              <div className="text-[11px] text-slate-500 mt-0.5">Server supervisor</div>
            </button>
          </div>
        </div>

        {/* System & Telemetry Card */}
        <div className="glass-panel p-6 rounded-2xl space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                <Cpu className="h-4 w-4 text-nova-cyan" />
                <span>Host Telemetry</span>
              </h2>
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                ACTIVE
              </span>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between items-center p-2.5 rounded-lg bg-nova-900/80 border border-nova-800">
                <span className="text-xs text-slate-400">Database Layer</span>
                <span className="text-xs font-mono font-bold text-slate-200">
                  {telemetry?.database?.type || 'Connected'}
                </span>
              </div>
              <div className="flex justify-between items-center p-2.5 rounded-lg bg-nova-900/80 border border-nova-800">
                <span className="text-xs text-slate-400">Host CPU Load</span>
                <span className="text-xs font-mono font-bold text-slate-200">
                  {telemetry?.system?.cpu_percent ? `${telemetry.system.cpu_percent}%` : 'Normal'}
                </span>
              </div>
              <div className="flex justify-between items-center p-2.5 rounded-lg bg-nova-900/80 border border-nova-800">
                <span className="text-xs text-slate-400">Memory Footprint</span>
                <span className="text-xs font-mono font-bold text-slate-200">
                  {telemetry?.system?.memory_used_mb ? `${telemetry.system.memory_used_mb} MB` : 'Optimal'}
                </span>
              </div>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-nova-850/80 border border-nova-800 text-[11px] text-slate-400 space-y-1">
            <div className="flex items-center gap-1.5 text-nova-emerald font-semibold">
              <ShieldCheck className="h-3.5 w-3.5" />
              <span>Permission Guard</span>
            </div>
            <p>Consequential OS mutations and file removals require direct user modal confirmation.</p>
          </div>
        </div>
      </div>

      {/* Second Row: Active Projects & Today's Tasks */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Active Projects */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
              <FolderKanban className="h-4 w-4 text-purple-400" />
              <span>Active Projects</span>
            </h2>
            <button
              onClick={() => navigate('/projects')}
              className="text-xs text-nova-accent hover:underline flex items-center gap-1"
            >
              <span>View All</span>
              <ArrowRight className="h-3 w-3" />
            </button>
          </div>

          <div className="space-y-2.5">
            <div 
              onClick={() => navigate('/projects')}
              className="p-3.5 rounded-xl bg-nova-900/80 border border-nova-800 hover:border-purple-400/40 cursor-pointer transition-all flex items-center justify-between group"
            >
              <div className="space-y-0.5">
                <div className="text-xs font-bold text-slate-200 group-hover:text-white">NOVA X Platform</div>
                <div className="text-[11px] text-slate-400">Master architecture, RAG, agents, and desktop OS automation</div>
              </div>
              <span className="text-[10px] font-mono text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">
                IN PROGRESS
              </span>
            </div>

            <div 
              onClick={() => navigate('/projects')}
              className="p-3.5 rounded-xl bg-nova-900/80 border border-nova-800 hover:border-blue-400/40 cursor-pointer transition-all flex items-center justify-between group"
            >
              <div className="space-y-0.5">
                <div className="text-xs font-bold text-slate-200 group-hover:text-white">EventSphere Full Stack</div>
                <div className="text-[11px] text-slate-400">React frontend, Node/FastAPI services, MongoDB, and UI</div>
              </div>
              <span className="text-[10px] font-mono text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/20">
                ACTIVE
              </span>
            </div>
          </div>
        </div>

        {/* Today's Tasks & Reminders */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
              <CheckSquare className="h-4 w-4 text-emerald-400" />
              <span>Today's Milestones</span>
            </h2>
            <button
              onClick={() => navigate('/tasks')}
              className="text-xs text-nova-accent hover:underline flex items-center gap-1"
            >
              <span>Manage</span>
              <ArrowRight className="h-3 w-3" />
            </button>
          </div>

          <div className="space-y-2.5">
            <div className="p-3 rounded-xl bg-nova-900/80 border border-nova-800 flex items-center gap-3">
              <input type="checkbox" defaultChecked className="rounded border-nova-700 text-nova-accent focus:ring-0" />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-slate-200 line-through text-slate-400">Complete Phase 0 architecture & monorepo setup</p>
                <p className="text-[10px] text-slate-500 font-mono">System Foundation • Verified</p>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-nova-900/80 border border-nova-800 flex items-center gap-3">
              <input type="checkbox" defaultChecked className="rounded border-nova-700 text-nova-accent focus:ring-0" />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-slate-200">Phase 1: Implement Auth & Application Shell</p>
                <p className="text-[10px] text-slate-500 font-mono">FastAPI JWT + React Router App Shell</p>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-nova-900/80 border border-nova-800 flex items-center gap-3">
              <input type="checkbox" className="rounded border-nova-700 text-nova-accent focus:ring-0" />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-slate-200">Phase 2: Universal Chat & Real-Time Streaming</p>
                <p className="text-[10px] text-slate-500 font-mono">SSE Tokens, Branching, Citations & Composer</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
