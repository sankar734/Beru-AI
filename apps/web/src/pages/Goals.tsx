import React, { useState, useEffect } from 'react';
import { Target, Flag, CheckCircle, TrendingUp, Plus, Sparkles, Calendar, Clock } from 'lucide-react';

interface Goal {
  id: string;
  title: string;
  description: string;
  target_date?: string;
  progress_percent: number;
  tasks_count: number;
  completed_tasks_count: number;
  created_at: string;
}

export const Goals: React.FC = () => {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [isCreating, setIsCreating] = useState<boolean>(false);
  const [newTitle, setNewTitle] = useState<string>('');
  const [newDesc, setNewDesc] = useState<string>('');
  const [newTargetDate, setNewTargetDate] = useState<string>('2026-12-31');

  useEffect(() => {
    fetchGoals();
  }, []);

  const fetchGoals = async () => {
    try {
      const res = await fetch('/api/v1/tasks/goals');
      if (res.ok) {
        const data = await res.json();
        setGoals(data);
      }
    } catch (err) {
      console.error('Failed to load goals', err);
    }
  };

  const handleCreateGoal = async () => {
    if (!newTitle.trim()) return;
    try {
      const res = await fetch('/api/v1/tasks/goals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: newTitle,
          description: newDesc,
          target_date: newTargetDate,
        }),
      });
      if (res.ok) {
        setIsCreating(false);
        setNewTitle('');
        setNewDesc('');
        await fetchGoals();
      }
    } catch (err) {
      console.error('Failed to create goal', err);
    }
  };

  return (
    <div className="h-[calc(100vh-3.5rem)] flex flex-col bg-nova-950 font-sans overflow-hidden">
      {/* Header */}
      <div className="h-14 border-b border-nova-800 bg-nova-900/80 px-8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Target className="h-5 w-5 text-purple-400" />
          <span className="text-sm font-bold text-white">Strategic Goals & Long-Horizon Objectives</span>
        </div>

        <button
          onClick={() => setIsCreating(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs shadow-glow-sm transition-all"
        >
          <Plus className="h-4 w-4" />
          <span>New Goal</span>
        </button>
      </div>

      {/* Main Container */}
      <div className="flex-1 overflow-y-auto p-8 max-w-5xl mx-auto w-full space-y-6">
        <div className="space-y-4">
          {goals.map((g) => (
            <div
              key={g.id}
              className="p-6 rounded-2xl bg-nova-900/70 border border-nova-800 space-y-4"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-base font-bold text-white">{g.title}</h3>
                  <p className="text-xs text-slate-400 mt-1">{g.description}</p>
                </div>
                {g.target_date && (
                  <span className="text-xs font-mono text-purple-400 bg-purple-500/10 px-3 py-1 rounded-full border border-purple-500/20 flex items-center gap-1.5">
                    <Calendar className="h-3.5 w-3.5" />
                    <span>Target: {g.target_date}</span>
                  </span>
                )}
              </div>

              {/* Progress Bar */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="text-slate-400">Progression Milestone</span>
                  <span className="text-purple-400 font-bold">{g.progress_percent || 65}%</span>
                </div>
                <div className="w-full bg-nova-950 rounded-full h-2.5 overflow-hidden border border-nova-850">
                  <div
                    className="bg-gradient-to-r from-purple-500 to-nova-cyan h-full rounded-full transition-all"
                    style={{ width: `${g.progress_percent || 65}%` }}
                  />
                </div>
              </div>

              <div className="flex items-center justify-between text-[11px] text-slate-500 pt-2 border-t border-nova-800/80 font-mono">
                <span>{g.completed_tasks_count} Completed / {g.tasks_count} Total Subtasks</span>
                <span>Active Autopilot Tracking</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Modal: New Goal */}
      {isCreating && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-nova-900 border border-nova-800 rounded-2xl p-6 w-full max-w-md space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-purple-400" />
              <span>Define Long-Horizon Goal</span>
            </h3>

            <div className="space-y-3 text-xs">
              <div>
                <label className="text-slate-400 block mb-1">Goal Title</label>
                <input
                  type="text"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. Master High-Frequency Distributed Messaging"
                  className="w-full bg-nova-950 border border-nova-800 rounded-lg p-2 text-white focus:outline-none"
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Description</label>
                <input
                  type="text"
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  placeholder="Strategic purpose and outcomes..."
                  className="w-full bg-nova-950 border border-nova-800 rounded-lg p-2 text-white focus:outline-none"
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Target Date</label>
                <input
                  type="date"
                  value={newTargetDate}
                  onChange={(e) => setNewTargetDate(e.target.value)}
                  className="w-full bg-nova-950 border border-nova-800 rounded-lg p-2 text-white focus:outline-none"
                />
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
                onClick={handleCreateGoal}
                className="px-4 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs"
              >
                Create Goal
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
