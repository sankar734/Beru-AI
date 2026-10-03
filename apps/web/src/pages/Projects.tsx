import React, { useEffect, useState } from 'react';
import { FolderKanban, Plus, FileText, Trash2, CheckCircle2, X, Sparkles } from 'lucide-react';

interface Project {
  id: string;
  name: string;
  description: string;
  system_instructions: string;
  custom_rules: string[];
  file_count: number;
  created_at: string;
}

export const Projects: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [systemInstructions, setSystemInstructions] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const fetchProjects = async () => {
    const token = localStorage.getItem('nova_token');
    try {
      const res = await fetch('/api/v1/projects', {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) {
        const data = await res.json();
        setProjects(data);
      }
    } catch {}
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setIsLoading(true);
    const token = localStorage.getItem('nova_token');

    try {
      const res = await fetch('/api/v1/projects', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          name,
          description,
          system_instructions: systemInstructions,
        }),
      });
      if (res.ok) {
        await fetchProjects();
        setIsModalOpen(false);
        setName('');
        setDescription('');
        setSystemInstructions('');
      }
    } catch {}
    finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    const token = localStorage.getItem('nova_token');
    try {
      const res = await fetch(`/api/v1/projects/${id}`, {
        method: 'DELETE',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) {
        setProjects(projects.filter((p) => p.id !== id));
      }
    } catch {}
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 font-sans animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h1 className="text-2xl font-extrabold text-white flex items-center gap-2.5">
            <FolderKanban className="h-6 w-6 text-purple-400" />
            <span>Projects & Context Spaces</span>
          </h1>
          <p className="text-xs text-slate-400">
            Isolated contextual workspaces with custom system instructions, persistent files, and scoped memory.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs shadow-glow-sm transition-all"
        >
          <Plus className="h-4 w-4" />
          <span>New Project</span>
        </button>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {projects.length === 0 ? (
          <div className="md:col-span-2 p-12 text-center text-xs text-slate-500 glass-panel rounded-2xl border border-nova-800 space-y-2">
            <FolderKanban className="h-8 w-8 text-slate-600 mx-auto" />
            <p>No projects created yet. Click "New Project" to configure an isolated context workspace.</p>
          </div>
        ) : (
          projects.map((proj) => (
            <div
              key={proj.id}
              className="glass-panel p-6 rounded-2xl border border-nova-750 hover:border-purple-400/40 transition-all space-y-3 relative group"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-sm font-bold text-white">{proj.name}</h3>
                  <p className="text-xs text-slate-400 mt-0.5 line-clamp-2">
                    {proj.description || 'No description provided.'}
                  </p>
                </div>
                <button
                  onClick={() => handleDelete(proj.id)}
                  className="opacity-0 group-hover:opacity-100 p-1.5 text-slate-500 hover:text-rose-400 hover:bg-nova-850 rounded-lg transition-all"
                  title="Delete Project"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>

              {proj.system_instructions && (
                <div className="p-2.5 rounded-xl bg-nova-900/60 border border-nova-800 text-[11px] text-slate-300 font-mono line-clamp-2">
                  <span className="text-purple-400 font-bold">Instructions: </span>
                  {proj.system_instructions}
                </div>
              )}

              <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 pt-2 border-t border-nova-800/80">
                <span>{proj.file_count} Files Linked</span>
                <span>Active Scope</span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Creation Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in">
          <div className="w-full max-w-lg bg-nova-900 border border-nova-700 rounded-2xl p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-nova-800">
              <h2 className="text-sm font-bold text-white">Create New Project Space</h2>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-500 hover:text-slate-300">
                <X className="h-4 w-4" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Project Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g., EventSphere Web Application"
                  required
                  className="w-full bg-nova-950 border border-nova-800 rounded-xl px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-purple-400"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Description</label>
                <textarea
                  rows={2}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Brief description of project purpose and architecture..."
                  className="w-full bg-nova-950 border border-nova-800 rounded-xl px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-purple-400 resize-none"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Persistent System Instructions</label>
                <textarea
                  rows={3}
                  value={systemInstructions}
                  onChange={(e) => setSystemInstructions(e.target.value)}
                  placeholder="e.g., Always use TypeScript strict mode. Write modular components using Tailwind CSS..."
                  className="w-full bg-nova-950 border border-nova-800 rounded-xl px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-purple-400 resize-none font-mono"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-nova-850 hover:bg-nova-800 text-xs text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isLoading || !name.trim()}
                  className="px-5 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs shadow-glow-sm disabled:opacity-50"
                >
                  {isLoading ? 'Creating...' : 'Create Project'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
