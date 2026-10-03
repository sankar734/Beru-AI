import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Search, 
  MessageSquarePlus, 
  Compass, 
  Code2, 
  FolderKanban, 
  Sparkles, 
  Laptop, 
  Bot, 
  Workflow, 
  CheckSquare, 
  Settings, 
  X 
} from 'lucide-react';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        if (isOpen) onClose();
        else onClose(); // parent handles toggle
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const actions = [
    { title: 'New Chat', desc: 'Start a fresh conversation with NOVA X', icon: MessageSquarePlus, path: '/chat', category: 'General' },
    { title: 'Search Mode', desc: 'Perform grounded web and academic search', icon: Search, path: '/search', category: 'General' },
    { title: 'Deep Research', desc: 'Launch multi-source comprehensive research job', icon: Compass, path: '/research', category: 'Intelligence' },
    { title: 'Code Workspace', desc: 'Open isolated code editor and runtime', icon: Code2, path: '/code', category: 'Development' },
    { title: 'Studio Artifacts', desc: 'Create documents, presentations, and web apps', icon: Sparkles, path: '/studio', category: 'Creation' },
    { title: 'Projects', desc: 'Manage project context, files, and tasks', icon: FolderKanban, path: '/projects', category: 'Workspace' },
    { title: 'Desktop Companion', desc: 'Inspect local machine status and apps', icon: Laptop, path: '/desktop', category: 'Desktop' },
    { title: 'Developer Agent', desc: 'Supervise dev servers, build errors, and git', icon: Code2, path: '/desktop/developer', category: 'Desktop' },
    { title: 'Autonomous Agents', desc: 'Run multi-step goal execution agent', icon: Bot, path: '/agents', category: 'Automation' },
    { title: 'Workflows', desc: 'Visual automation DAG builder', icon: Workflow, path: '/workflows', category: 'Automation' },
    { title: 'Tasks & Goals', desc: 'Track milestones and daily todos', icon: CheckSquare, path: '/tasks', category: 'Productivity' },
    { title: 'Settings', desc: 'Configure models, privacy, and desktop access', icon: Settings, path: '/settings', category: 'Preferences' },
  ];

  const filtered = actions.filter(a => 
    a.title.toLowerCase().includes(query.toLowerCase()) || 
    a.desc.toLowerCase().includes(query.toLowerCase()) ||
    a.category.toLowerCase().includes(query.toLowerCase())
  );

  const handleSelect = (path: string) => {
    navigate(path);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-start justify-center pt-24 p-4 animate-in fade-in duration-150">
      <div className="w-full max-w-xl bg-nova-900 border border-nova-700 rounded-2xl shadow-2xl overflow-hidden flex flex-col">
        {/* Search Input Bar */}
        <div className="flex items-center px-4 py-3.5 border-b border-nova-800 gap-3">
          <Search className="h-5 w-5 text-nova-accent shrink-0" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type a command or search actions... (ESC to close)"
            className="w-full bg-transparent text-sm text-slate-100 placeholder-slate-500 focus:outline-none"
            autoFocus
          />
          <button onClick={onClose} className="text-slate-500 hover:text-slate-300">
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Results List */}
        <div className="max-h-80 overflow-y-auto p-2 space-y-1">
          {filtered.length === 0 ? (
            <div className="p-6 text-center text-xs text-slate-500">
              No matching commands found for "{query}".
            </div>
          ) : (
            filtered.map((action, i) => {
              const Icon = action.icon;
              return (
                <button
                  key={i}
                  onClick={() => handleSelect(action.path)}
                  className="w-full flex items-center justify-between p-2.5 rounded-xl hover:bg-nova-800 text-left transition-colors group"
                >
                  <div className="flex items-center gap-3">
                    <div className="h-8 w-8 rounded-lg bg-nova-850 border border-nova-800 flex items-center justify-center text-slate-400 group-hover:text-nova-accent group-hover:border-nova-accent/40 transition-colors">
                      <Icon className="h-4 w-4" />
                    </div>
                    <div>
                      <div className="text-xs font-semibold text-slate-200 group-hover:text-white">
                        {action.title}
                      </div>
                      <div className="text-[11px] text-slate-400 line-clamp-1">
                        {action.desc}
                      </div>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono text-slate-500 bg-nova-950 px-2 py-0.5 rounded border border-nova-800">
                    {action.category}
                  </span>
                </button>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-2 border-t border-nova-800 bg-nova-950/60 flex items-center justify-between text-[11px] text-slate-500">
          <span>Navigation: <kbd className="bg-nova-900 border border-nova-800 px-1 rounded text-[10px]">↑</kbd> <kbd className="bg-nova-900 border border-nova-800 px-1 rounded text-[10px]">↓</kbd> to select</span>
          <span>Open: <kbd className="bg-nova-900 border border-nova-800 px-1 rounded text-[10px]">ENTER</kbd></span>
        </div>
      </div>
    </div>
  );
};
