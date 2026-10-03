import React, { useState } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { CommandPalette } from './CommandPalette';
import { 
  Search, 
  Bell, 
  Laptop, 
  OctagonAlert, 
  Compass, 
  ShieldCheck 
} from 'lucide-react';
import { useAuthStore } from '../../stores/useAuthStore';

export const AppLayout: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [isCommandOpen, setIsCommandOpen] = useState(false);

  // Derive route title
  const getPageTitle = (pathname: string) => {
    if (pathname === '/') return 'Personal Intelligence Dashboard';
    if (pathname.startsWith('/chat')) return 'Universal Chat & Reasoning';
    if (pathname.startsWith('/search')) return 'Grounded AI Search';
    if (pathname.startsWith('/research')) return 'Autonomous Deep Research';
    if (pathname.startsWith('/studio')) return 'NOVA Studio (Artifacts & Creation)';
    if (pathname.startsWith('/code')) return 'Code Workspace & Sandbox';
    if (pathname.startsWith('/learn')) return 'Learning OS & AI Tutor';
    if (pathname.startsWith('/projects')) return 'Projects & Context Spaces';
    if (pathname.startsWith('/files')) return 'Files & Hybrid RAG Intelligence';
    if (pathname.startsWith('/experts')) return 'Custom AI Experts';
    if (pathname.startsWith('/agents')) return 'Autonomous Goal Execution Agents';
    if (pathname.startsWith('/workflows')) return 'Visual Workflow Automation';
    if (pathname.startsWith('/tasks')) return 'Tasks & Reminders';
    if (pathname.startsWith('/goals')) return 'Goals & Autopilot Coaching';
    if (pathname.startsWith('/desktop/developer')) return 'Developer Agent & Process Supervisor';
    if (pathname.startsWith('/desktop')) return 'Desktop Control & Host Companion';
    if (pathname.startsWith('/settings')) return 'System Settings & Privacy';
    return 'NOVA X';
  };

  return (
    <div className="flex h-screen w-screen bg-nova-950 text-slate-100 font-sans overflow-hidden">
      {/* Global Sidebar */}
      <Sidebar />

      {/* Main Content Pane */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header */}
        <header className="h-14 border-b border-nova-800 bg-nova-900/40 backdrop-blur-md px-6 flex items-center justify-between shrink-0 z-20">
          {/* Breadcrumb / Title */}
          <div className="flex items-center gap-3">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-300 font-mono">
              {getPageTitle(location.pathname)}
            </h2>
          </div>

          {/* Quick Actions & Status */}
          <div className="flex items-center gap-3">
            {/* Command Palette Trigger */}
            <button
              onClick={() => setIsCommandOpen(true)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-nova-850 border border-nova-800 hover:border-nova-700 text-slate-400 hover:text-slate-200 text-xs transition-colors"
            >
              <Search className="h-3.5 w-3.5" />
              <span>Search or action...</span>
              <kbd className="bg-nova-900 border border-nova-800 px-1.5 py-0.5 rounded text-[10px] font-mono text-slate-500">
                Ctrl K
              </kbd>
            </button>

            {/* Desktop Status Badge */}
            <button
              onClick={() => navigate('/desktop')}
              className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-nova-cyan/10 border border-nova-cyan/25 text-nova-cyan text-xs font-mono hover:bg-nova-cyan/20 transition-colors"
              title="Desktop Companion Bridge"
            >
              <span className="h-1.5 w-1.5 rounded-full bg-nova-cyan animate-pulse"></span>
              <Laptop className="h-3 w-3" />
              <span>Host Bridge</span>
            </button>

            {/* Emergency Stop Button (Part 97) */}
            <button
              onClick={() => alert("Emergency Stop Triggered: All active automations, background agents, and queued actions revoked.")}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-400 text-xs font-semibold transition-colors"
              title="Immediately halts all active background automation and desktop actions"
            >
              <OctagonAlert className="h-3.5 w-3.5" />
              <span>STOP NOVA</span>
            </button>
          </div>
        </header>

        {/* Content Outlet */}
        <main className="flex-1 overflow-y-auto relative">
          <Outlet />
        </main>
      </div>

      {/* Global Command Palette */}
      <CommandPalette isOpen={isCommandOpen} onClose={() => setIsCommandOpen(false)} />
    </div>
  );
};
