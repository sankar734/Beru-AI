import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { 
  Sparkles, 
  Plus, 
  Search, 
  Compass, 
  Paintbrush, 
  Code2, 
  BookOpen, 
  FolderKanban, 
  FileText, 
  BrainCircuit, 
  Bot, 
  Workflow, 
  CheckSquare, 
  Target, 
  Laptop, 
  Terminal, 
  Settings, 
  LogOut, 
  MessageSquare,
  ShieldCheck 
} from 'lucide-react';
import { useAuthStore } from '../../stores/useAuthStore';

export const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItemClass = ({ isActive }: { isActive: boolean }) =>
    `flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
      isActive
        ? 'bg-nova-accent/15 text-nova-accent border border-nova-accent/30 shadow-sm'
        : 'text-slate-400 hover:text-slate-200 hover:bg-nova-850/80'
    }`;

  return (
    <aside className="w-64 border-r border-nova-800 bg-nova-900/80 backdrop-blur-xl flex flex-col justify-between h-screen select-none shrink-0">
      {/* Top Branding & Main Actions */}
      <div className="flex flex-col overflow-y-auto p-3.5 space-y-5">
        {/* Brand Header */}
        <div className="flex items-center justify-between px-1">
          <div 
            onClick={() => navigate('/')}
            className="flex items-center gap-2.5 cursor-pointer group"
          >
            <div className="h-8 w-8 rounded-xl bg-gradient-to-tr from-nova-accent to-nova-cyan flex items-center justify-center shadow-glow-sm group-hover:scale-105 transition-transform">
              <Sparkles className="h-4 w-4 text-white" />
            </div>
            <div>
              <span className="font-extrabold text-sm tracking-wider text-white">NOVA X</span>
              <p className="text-[9px] text-nova-cyan uppercase font-mono tracking-widest leading-none">Intelligence OS</p>
            </div>
          </div>
        </div>

        {/* New Chat Button */}
        <button
          onClick={() => navigate('/chat')}
          className="flex items-center justify-center gap-2 w-full py-2.5 px-3 rounded-xl bg-gradient-to-r from-nova-accent to-blue-600 hover:from-blue-600 hover:to-nova-accent text-white font-semibold text-xs shadow-glow-sm hover:shadow-glow-md transition-all active:scale-[0.98]"
        >
          <Plus className="h-4 w-4" />
          <span>New Chat</span>
        </button>

        {/* Primary Modes */}
        <div className="space-y-0.5">
          <NavLink to="/search" className={navItemClass}>
            <Search className="h-3.5 w-3.5 text-nova-cyan" />
            <span>Search</span>
          </NavLink>
          <NavLink to="/research" className={navItemClass}>
            <Compass className="h-3.5 w-3.5 text-blue-400" />
            <span>Research</span>
          </NavLink>
          <NavLink to="/studio" className={navItemClass}>
            <Paintbrush className="h-3.5 w-3.5 text-purple-400" />
            <span>Create (Studio)</span>
          </NavLink>
          <NavLink to="/code" className={navItemClass}>
            <Code2 className="h-3.5 w-3.5 text-emerald-400" />
            <span>Code</span>
          </NavLink>
          <NavLink to="/learn" className={navItemClass}>
            <BookOpen className="h-3.5 w-3.5 text-amber-400" />
            <span>Learn</span>
          </NavLink>
        </div>

        {/* WORKSPACE SECTION */}
        <div className="space-y-1">
          <div className="px-2 text-[10px] font-mono font-semibold uppercase tracking-wider text-slate-500">
            Workspace
          </div>
          <div className="space-y-0.5">
            <NavLink to="/projects" className={navItemClass}>
              <FolderKanban className="h-3.5 w-3.5 text-slate-400" />
              <span>Projects</span>
            </NavLink>
            <NavLink to="/files" className={navItemClass}>
              <FileText className="h-3.5 w-3.5 text-slate-400" />
              <span>Files & RAG</span>
            </NavLink>
            <NavLink to="/experts" className={navItemClass}>
              <BrainCircuit className="h-3.5 w-3.5 text-slate-400" />
              <span>Custom Experts</span>
            </NavLink>
          </div>
        </div>

        {/* AUTOMATION SECTION */}
        <div className="space-y-1">
          <div className="px-2 text-[10px] font-mono font-semibold uppercase tracking-wider text-slate-500">
            Automation
          </div>
          <div className="space-y-0.5">
            <NavLink to="/agents" className={navItemClass}>
              <Bot className="h-3.5 w-3.5 text-slate-400" />
              <span>Agents</span>
            </NavLink>
            <NavLink to="/workflows" className={navItemClass}>
              <Workflow className="h-3.5 w-3.5 text-slate-400" />
              <span>Workflows</span>
            </NavLink>
            <NavLink to="/tasks" className={navItemClass}>
              <CheckSquare className="h-3.5 w-3.5 text-slate-400" />
              <span>Tasks & Reminders</span>
            </NavLink>
            <NavLink to="/goals" className={navItemClass}>
              <Target className="h-3.5 w-3.5 text-slate-400" />
              <span>Goals & Autopilot</span>
            </NavLink>
          </div>
        </div>

        {/* DESKTOP SECTION */}
        <div className="space-y-1">
          <div className="px-2 text-[10px] font-mono font-semibold uppercase tracking-wider text-slate-500">
            Desktop Control
          </div>
          <div className="space-y-0.5">
            <NavLink to="/desktop" className={navItemClass}>
              <Laptop className="h-3.5 w-3.5 text-nova-cyan" />
              <span>Computer</span>
            </NavLink>
            <NavLink to="/desktop/developer" className={navItemClass}>
              <Terminal className="h-3.5 w-3.5 text-nova-emerald" />
              <span>Developer Mode</span>
            </NavLink>
          </div>
        </div>

        {/* RECENT CHATS */}
        <div className="space-y-1">
          <div className="px-2 text-[10px] font-mono font-semibold uppercase tracking-wider text-slate-500 flex items-center justify-between">
            <span>Recent Chats</span>
          </div>
          <div className="space-y-0.5">
            <button
              onClick={() => navigate('/chat/welcome')}
              className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-left text-xs text-slate-400 hover:text-slate-200 hover:bg-nova-850 truncate"
            >
              <MessageSquare className="h-3 w-3 shrink-0 text-slate-500" />
              <span className="truncate">Architecting NOVA X</span>
            </button>
            <button
              onClick={() => navigate('/chat/research-demo')}
              className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-left text-xs text-slate-400 hover:text-slate-200 hover:bg-nova-850 truncate"
            >
              <MessageSquare className="h-3 w-3 shrink-0 text-slate-500" />
              <span className="truncate">Deep Research Workflow</span>
            </button>
          </div>
        </div>
      </div>

      {/* Footer Profile & Security */}
      <div className="p-3 border-t border-nova-800 bg-nova-950/40 space-y-2">
        {/* Security Tag */}
        <div className="flex items-center gap-2 px-2 py-1 rounded bg-nova-850/60 text-[10px] text-nova-emerald font-mono">
          <ShieldCheck className="h-3.5 w-3.5 shrink-0" />
          <span className="truncate">Zero-Trust Policy Active</span>
        </div>

        {/* User bar */}
        <div className="flex items-center justify-between pt-1">
          <div className="flex items-center gap-2 min-w-0">
            <div className="h-7 w-7 rounded-full bg-nova-accent/20 border border-nova-accent/40 flex items-center justify-center text-xs font-bold text-nova-accent shrink-0">
              {user?.name ? user.name[0].toUpperCase() : 'O'}
            </div>
            <div className="min-w-0">
              <p className="text-xs font-semibold text-slate-200 truncate">{user?.name || 'Operator'}</p>
              <p className="text-[10px] text-slate-500 truncate">{user?.email || 'operator@novax'}</p>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => navigate('/settings')}
              title="Settings"
              className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-nova-850 rounded-lg transition-colors"
            >
              <Settings className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={handleLogout}
              title="Sign Out"
              className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-nova-850 rounded-lg transition-colors"
            >
              <LogOut className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>
    </aside>
  );
};
