import React, { useState, useEffect } from 'react';
import {
  CheckSquare,
  Plus,
  Calendar,
  Clock,
  Bot,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Play,
  Trash2,
  Layers,
  X,
} from 'lucide-react';

interface Task {
  id: string;
  goal_id?: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  due_date?: string;
  assigned_agent_id?: string;
  created_at: string;
  updated_at: string;
}

export const Tasks: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [filterStatus, setFilterStatus] = useState<string>('ALL');
  const [isCreating, setIsCreating] = useState<boolean>(false);
  const [newTitle, setNewTitle] = useState<string>('');
  const [newDesc, setNewDesc] = useState<string>('');
  const [newPriority, setNewPriority] = useState<string>('HIGH');
  const [delegatingTaskId, setDelegatingTaskId] = useState<string | null>(null);

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      const res = await fetch('/api/v1/tasks');
      if (res.ok) {
        const data = await res.json();
        setTasks(data);
      }
    } catch (err) {
      console.error('Failed to load tasks', err);
    }
  };

  const handleToggleStatus = async (task: Task) => {
    const nextStatus = task.status === 'COMPLETED' ? 'TODO' : 'COMPLETED';
    try {
      const res = await fetch(`/api/v1/tasks/${task.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: nextStatus }),
      });
      if (res.ok) {
        const updated = await res.json();
        setTasks(tasks.map((t) => (t.id === task.id ? updated : t)));
      }
    } catch (err) {
      console.error('Failed to update task', err);
    }
  };

  const handleDelegateAgent = async (taskId: string) => {
    setDelegatingTaskId(taskId);
    try {
      const res = await fetch(`/api/v1/tasks/${taskId}/dispatch-agent`, {
        method: 'POST',
      });
      if (res.ok) {
        await fetchTasks();
      }
    } catch (err) {
      console.error('Failed to dispatch agent', err);
    } finally {
      setDelegatingTaskId(null);
    }
  };

  const handleCreateTask = async () => {
    if (!newTitle.trim()) return;
    try {
      const res = await fetch('/api/v1/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: newTitle,
          description: newDesc,
          priority: newPriority,
        }),
      });
      if (res.ok) {
        setIsCreating(false);
        setNewTitle('');
        setNewDesc('');
        await fetchTasks();
      }
    } catch (err) {
      console.error('Failed to create task', err);
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    try {
      const res = await fetch(`/api/v1/tasks/${taskId}`, { method: 'DELETE' });
      if (res.ok) {
        setTasks(tasks.filter((t) => t.id !== taskId));
      }
    } catch (err) {
      console.error('Failed to delete task', err);
    }
  };

  const filteredTasks =
    filterStatus === 'ALL'
      ? tasks
      : tasks.filter((t) => t.status === filterStatus);

  const getPriorityBadge = (p: string) => {
    switch (p.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/30';
      case 'HIGH':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/30';
      case 'MEDIUM':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      default:
        return 'bg-slate-800 text-slate-400 border-slate-700';
    }
  };

  return (
    <div className="h-[calc(100vh-3.5rem)] flex flex-col bg-nova-950 font-sans overflow-hidden">
      {/* Header */}
      <div className="h-14 border-b border-nova-800 bg-nova-900/80 px-8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <CheckSquare className="h-5 w-5 text-emerald-400" />
          <span className="text-sm font-bold text-white">Tasks & Strategic Execution Backlog</span>
        </div>

        <button
          onClick={() => setIsCreating(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs shadow-glow-sm transition-all"
        >
          <Plus className="h-4 w-4" />
          <span>New Task</span>
        </button>
      </div>

      {/* Main Container */}
      <div className="flex-1 overflow-y-auto p-8 max-w-5xl mx-auto w-full space-y-6">
        {/* Filters */}
        <div className="flex items-center gap-2 border-b border-nova-800 pb-3">
          {['ALL', 'TODO', 'IN_PROGRESS', 'COMPLETED'].map((s) => (
            <button
              key={s}
              onClick={() => setFilterStatus(s)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                filterStatus === s
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-nova-900'
              }`}
            >
              {s}
            </button>
          ))}
        </div>

        {/* Task List */}
        <div className="space-y-3">
          {filteredTasks.map((t) => (
            <div
              key={t.id}
              className={`p-4 rounded-xl border transition-all flex items-center justify-between gap-4 ${
                t.status === 'COMPLETED'
                  ? 'bg-nova-900/30 border-nova-850 opacity-70'
                  : 'bg-nova-900/70 border-nova-800 hover:border-emerald-500/40'
              }`}
            >
              <div className="flex items-start gap-3 flex-1 min-w-0">
                <input
                  type="checkbox"
                  checked={t.status === 'COMPLETED'}
                  onChange={() => handleToggleStatus(t)}
                  className="mt-0.5 rounded border-nova-700 text-emerald-500 focus:ring-0 cursor-pointer"
                />
                <div className="space-y-1 min-w-0">
                  <div
                    className={`text-xs font-semibold text-white ${
                      t.status === 'COMPLETED' ? 'line-through text-slate-500' : ''
                    }`}
                  >
                    {t.title}
                  </div>
                  {t.description && (
                    <p className="text-[11px] text-slate-400 line-clamp-1">{t.description}</p>
                  )}
                  {t.assigned_agent_id && (
                    <span className="inline-flex items-center gap-1 text-[10px] font-mono text-blue-400 bg-blue-500/10 px-2 py-0.2 rounded border border-blue-500/20">
                      <Bot className="h-3 w-3" />
                      <span>Delegated: {t.assigned_agent_id}</span>
                    </span>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-3 shrink-0">
                <span
                  className={`text-[10px] font-mono px-2 py-0.5 rounded border uppercase font-bold ${getPriorityBadge(
                    t.priority
                  )}`}
                >
                  {t.priority}
                </span>

                {t.status !== 'COMPLETED' && (
                  <button
                    onClick={() => handleDelegateAgent(t.id)}
                    disabled={delegatingTaskId === t.id}
                    title="Delegate to Autonomous AI Agent"
                    className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 text-xs font-semibold border border-blue-500/30 transition-colors"
                  >
                    <Bot className={`h-3.5 w-3.5 ${delegatingTaskId === t.id ? 'animate-spin' : ''}`} />
                    <span>{delegatingTaskId === t.id ? 'Delegating...' : 'Agent Exec'}</span>
                  </button>
                )}

                <button
                  onClick={() => handleDeleteTask(t.id)}
                  className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-nova-850 transition-colors"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Modal: New Task */}
      {isCreating && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-nova-900 border border-nova-800 rounded-2xl p-6 w-full max-w-md space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-emerald-400" />
              <span>Create Execution Task</span>
            </h3>

            <div className="space-y-3 text-xs">
              <div>
                <label className="text-slate-400 block mb-1">Task Title</label>
                <input
                  type="text"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. Profile cache invalidation latencies"
                  className="w-full bg-nova-950 border border-nova-800 rounded-lg p-2 text-white focus:outline-none"
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Description</label>
                <input
                  type="text"
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  placeholder="Specific requirements or bounds..."
                  className="w-full bg-nova-950 border border-nova-800 rounded-lg p-2 text-white focus:outline-none"
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Priority</label>
                <select
                  value={newPriority}
                  onChange={(e) => setNewPriority(e.target.value)}
                  className="w-full bg-nova-950 border border-nova-800 rounded-lg p-2 text-white focus:outline-none"
                >
                  <option value="CRITICAL">CRITICAL</option>
                  <option value="HIGH">HIGH</option>
                  <option value="MEDIUM">MEDIUM</option>
                  <option value="LOW">LOW</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setIsCreating(false)}
                className="px-3 py-1.5 rounded-lg bg-nova-800 text-slate-300 text-xs"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateTask}
                className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs"
              >
                Create Task
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
