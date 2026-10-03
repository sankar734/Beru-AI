import React, { useState, useEffect } from 'react';
import {
  Bot,
  Play,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Sparkles,
  ShieldAlert,
  ArrowRight,
  Terminal,
  FileCheck,
  XCircle,
  RotateCw,
  Plus,
  Lock,
} from 'lucide-react';

interface AgentStep {
  step_number: number;
  title: string;
  thought: string;
  tool_name?: string;
  tool_params?: Record<string, any>;
  risk_level: number;
  requires_approval: boolean;
  approval_request_id?: string;
  tool_result?: Record<string, any>;
  verification?: {
    verified: boolean;
    details: string;
    observed_state?: any;
  };
  status: string;
  duration_ms: number;
}

interface AgentRun {
  id: string;
  goal: string;
  mode: string;
  status: string;
  max_steps: number;
  current_step: number;
  steps: AgentStep[];
  final_summary?: string;
  pending_approval_id?: string;
  created_at: string;
  updated_at: string;
}

export const Agents: React.FC = () => {
  const [runs, setRuns] = useState<AgentRun[]>([]);
  const [activeRun, setActiveRun] = useState<AgentRun | null>(null);
  const [newGoal, setNewGoal] = useState<string>('Audit codebase security and build verification');
  const [isLaunching, setIsLaunching] = useState<boolean>(false);
  const [isAuthorizing, setIsAuthorizing] = useState<boolean>(false);

  useEffect(() => {
    fetchRuns();
  }, []);

  const fetchRuns = async () => {
    try {
      const res = await fetch('/api/v1/agents/runs');
      if (res.ok) {
        const data = await res.json();
        setRuns(data);
        if (data.length > 0 && !activeRun) {
          setActiveRun(data[data.length - 1]);
        }
      }
    } catch (err) {
      console.error('Failed to load agent runs', err);
    }
  };

  const handleLaunch = async (goalToLaunch?: string) => {
    const goal = goalToLaunch || newGoal;
    if (!goal.trim() || isLaunching) return;
    setIsLaunching(true);
    try {
      const res = await fetch('/api/v1/agents/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ goal, mode: 'AUTONOMOUS', max_steps: 8 }),
      });
      if (res.ok) {
        const runData = await res.json();
        setActiveRun(runData);
        await fetchRuns();
      }
    } catch (err) {
      console.error('Failed to launch agent', err);
    } finally {
      setIsLaunching(false);
    }
  };

  const handleDecision = async (approved: boolean) => {
    if (!activeRun || isAuthorizing) return;
    setIsAuthorizing(true);
    try {
      const res = await fetch(`/api/v1/agents/runs/${activeRun.id}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approved }),
      });
      if (res.ok) {
        const updated = await res.json();
        setActiveRun(updated);
        await fetchRuns();
      }
    } catch (err) {
      console.error('Failed to decide approval', err);
    } finally {
      setIsAuthorizing(false);
    }
  };

  return (
    <div className="h-[calc(100vh-3.5rem)] flex flex-col bg-nova-950 font-sans overflow-hidden">
      {/* Top Header */}
      <div className="h-14 border-b border-nova-800 bg-nova-900/80 px-8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Bot className="h-5 w-5 text-blue-400" />
          <span className="text-sm font-bold text-white">Autonomous Agent Mission Control</span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30">
            Zero-Trust Human Barrier
          </span>
        </div>

        {activeRun && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400 font-mono">Mission: {activeRun.id}</span>
            <span
              className={`text-[10px] font-mono font-bold px-2.5 py-0.5 rounded-full border ${
                activeRun.status === 'COMPLETED'
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                  : activeRun.status === 'AWAITING_APPROVAL'
                  ? 'bg-amber-500/20 text-amber-300 border-amber-500/40 animate-pulse'
                  : activeRun.status === 'STOPPED' || activeRun.status === 'FAILED'
                  ? 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                  : 'bg-blue-500/10 text-blue-400 border-blue-500/30'
              }`}
            >
              {activeRun.status}
            </span>
          </div>
        )}
      </div>

      {/* Main Content Layout */}
      <div className="flex-1 overflow-y-auto p-8 max-w-6xl mx-auto w-full space-y-6">
        {/* Mission Launcher Bar */}
        <div className="p-5 rounded-2xl bg-nova-900 border border-nova-800 space-y-3">
          <span className="text-xs font-bold text-white flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-blue-400" />
            <span>Launch Autonomous Mission</span>
          </span>
          <div className="flex items-center gap-3">
            <input
              type="text"
              value={newGoal}
              onChange={(e) => setNewGoal(e.target.value)}
              placeholder="Define high-level objective for autonomous agent..."
              className="flex-1 bg-nova-950 border border-nova-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-blue-500"
            />
            <button
              onClick={() => handleLaunch()}
              disabled={isLaunching || !newGoal.trim()}
              className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-bold text-xs rounded-xl shadow-glow-sm transition-all"
            >
              <Play className="h-3.5 w-3.5" />
              <span>{isLaunching ? 'Dispatching...' : 'Dispatch Agent'}</span>
            </button>
          </div>

          {/* Quick Presets */}
          <div className="flex items-center gap-2 pt-1 text-[11px] text-slate-400">
            <span className="text-slate-500">Presets:</span>
            {[
              'Audit codebase security and build verification',
              'Execute numerical formulation and aggregate statistical data',
              'Verify workspace system state and package health',
            ].map((preset, i) => (
              <button
                key={i}
                onClick={() => {
                  setNewGoal(preset);
                  handleLaunch(preset);
                }}
                className="px-2 py-0.5 rounded bg-nova-850 hover:bg-nova-800 text-slate-300 transition-colors"
              >
                {preset.split(' ')[0]} {preset.split(' ')[1]}...
              </button>
            ))}
          </div>
        </div>

        {/* HUMAN AUTHORIZATION BARRIER MODAL (Part 44) */}
        {activeRun && activeRun.status === 'AWAITING_APPROVAL' && (
          <div className="p-6 rounded-2xl bg-amber-500/10 border-2 border-amber-500/40 shadow-glow-md space-y-4 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-amber-500/20 text-amber-400">
                  <ShieldAlert className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <span>Human Authorization Required</span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/30 text-amber-200">
                      Risk Level 3 (Consequential Action)
                    </span>
                  </h3>
                  <p className="text-xs text-amber-300/80 mt-0.5">
                    Agent paused before executing consequential modification to host storage.
                  </p>
                </div>
              </div>
            </div>

            {/* Proposed Step Details */}
            {activeRun.steps[activeRun.current_step] && (
              <div className="p-4 rounded-xl bg-nova-950 border border-nova-800 text-xs space-y-2">
                <div className="flex items-center justify-between text-slate-400 font-mono text-[11px]">
                  <span>Step {activeRun.steps[activeRun.current_step].step_number}: {activeRun.steps[activeRun.current_step].title}</span>
                  <span className="text-amber-400">Tool: {activeRun.steps[activeRun.current_step].tool_name}</span>
                </div>
                <div className="text-slate-300 font-mono text-[11px] bg-nova-900 p-2.5 rounded border border-nova-850">
                  Parameters: {JSON.stringify(activeRun.steps[activeRun.current_step].tool_params, null, 2)}
                </div>
              </div>
            )}

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => handleDecision(false)}
                disabled={isAuthorizing}
                className="px-4 py-2 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 text-xs font-semibold border border-rose-500/30 transition-colors"
              >
                Deny & Abort Action
              </button>
              <button
                onClick={() => handleDecision(true)}
                disabled={isAuthorizing}
                className="px-5 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-nova-950 font-bold text-xs shadow-glow-sm transition-all"
              >
                {isAuthorizing ? 'Authorizing...' : 'Authorize Action to Proceed'}
              </button>
            </div>
          </div>
        )}

        {/* ACTIVE TRAJECTORY TIMELINE */}
        {activeRun && (
          <div className="p-6 rounded-2xl bg-nova-900 border border-nova-800 space-y-5">
            <div className="flex items-center justify-between border-b border-nova-800 pb-3">
              <div>
                <h3 className="text-sm font-bold text-white">{activeRun.goal}</h3>
                <span className="text-xs text-slate-400">
                  Mode: {activeRun.mode} • Steps completed: {activeRun.current_step} / {activeRun.steps.length}
                </span>
              </div>
            </div>

            {/* Steps Timeline */}
            <div className="space-y-4">
              {activeRun.steps.map((step) => (
                <div
                  key={step.step_number}
                  className={`p-4 rounded-xl border text-xs space-y-2 transition-all ${
                    step.status === 'COMPLETED'
                      ? 'bg-nova-950/70 border-emerald-500/30'
                      : step.status === 'AWAITING_APPROVAL'
                      ? 'bg-amber-500/10 border-amber-500/40'
                      : step.status === 'FAILED'
                      ? 'bg-rose-500/10 border-rose-500/40'
                      : 'bg-nova-950/40 border-nova-850'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 font-bold text-white">
                      {step.status === 'COMPLETED' ? (
                        <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                      ) : step.status === 'AWAITING_APPROVAL' ? (
                        <Lock className="h-4 w-4 text-amber-400" />
                      ) : step.status === 'FAILED' ? (
                        <XCircle className="h-4 w-4 text-rose-400" />
                      ) : (
                        <span className="h-4 w-4 rounded-full bg-slate-700 flex items-center justify-center text-[10px]">
                          {step.step_number}
                        </span>
                      )}
                      <span>
                        Step {step.step_number}: {step.title}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 font-mono text-[11px]">
                      <span className="text-[10px] px-2 py-0.5 rounded bg-nova-850 text-slate-400">
                        {step.tool_name} (Risk {step.risk_level})
                      </span>
                      {step.duration_ms > 0 && (
                        <span className="text-slate-500">{step.duration_ms}ms</span>
                      )}
                      <span
                        className={`text-[10px] font-bold ${
                          step.status === 'COMPLETED'
                            ? 'text-emerald-400'
                            : step.status === 'AWAITING_APPROVAL'
                            ? 'text-amber-400'
                            : 'text-slate-500'
                        }`}
                      >
                        {step.status}
                      </span>
                    </div>
                  </div>

                  <p className="text-slate-400 leading-relaxed pl-6">{step.thought}</p>

                  {/* Verification Result Badge */}
                  {step.verification && (
                    <div className="ml-6 p-2 rounded-lg bg-nova-900 border border-nova-850 text-[11px] text-emerald-300 flex items-center gap-2">
                      <FileCheck className="h-3.5 w-3.5 text-emerald-400 shrink-0" />
                      <span>{step.verification.details}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Final Summary Card */}
            {activeRun.final_summary && (
              <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-xs text-emerald-300 font-medium">
                ✓ {activeRun.final_summary}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
