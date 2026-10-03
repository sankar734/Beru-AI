import React, { useState, useEffect } from 'react';
import {
  Workflow as WorkflowIcon,
  Plus,
  Play,
  GitBranch,
  Clock,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Terminal,
  ArrowRight,
  Zap,
  Layers,
  X,
} from 'lucide-react';

interface WorkflowNode {
  id: string;
  name: string;
  type: string;
  config: Record<string, any>;
}

interface WorkflowEdge {
  source: string;
  target: string;
}

interface Workflow {
  id: string;
  name: string;
  description: string;
  trigger_type: string;
  enabled: boolean;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  created_at: string;
}

interface NodeTrace {
  node_id: string;
  node_name: string;
  type: string;
  status: string;
  output: any;
  duration_ms: number;
}

interface ExecutionResult {
  execution_id: string;
  workflow_id: string;
  workflow_name: string;
  status: string;
  traces: NodeTrace[];
  duration_ms: number;
  started_at: string;
  completed_at: string;
}

export const Workflows: React.FC = () => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [selectedWf, setSelectedWf] = useState<Workflow | null>(null);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [executionResult, setExecutionResult] = useState<ExecutionResult | null>(null);

  // New Workflow Modal
  const [isCreating, setIsCreating] = useState<boolean>(false);
  const [newName, setNewName] = useState<string>('');
  const [newDesc, setNewDesc] = useState<string>('');
  const [newTrigger, setNewTrigger] = useState<string>('MANUAL');

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const fetchWorkflows = async () => {
    try {
      const res = await fetch('/api/v1/workflows');
      if (res.ok) {
        const data = await res.json();
        setWorkflows(data);
        if (data.length > 0 && !selectedWf) {
          setSelectedWf(data[0]);
        }
      }
    } catch (err) {
      console.error('Failed to load workflows', err);
    }
  };

  const handleExecute = async (wf: Workflow) => {
    setSelectedWf(wf);
    setIsRunning(true);
    setExecutionResult(null);
    try {
      const res = await fetch(`/api/v1/workflows/${wf.id}/execute`, {
        method: 'POST',
      });
      if (res.ok) {
        const data = await res.json();
        setExecutionResult(data);
      }
    } catch (err) {
      console.error('Workflow execution failed', err);
    } finally {
      setIsRunning(false);
    }
  };

  const handleCreate = async () => {
    if (!newName.trim()) return;
    try {
      const res = await fetch('/api/v1/workflows', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newName,
          description: newDesc,
          trigger_type: newTrigger,
          nodes: [
            { id: 'n1', name: 'Start Trigger', type: 'TRIGGER', config: { type: newTrigger } },
            { id: 'n2', name: 'AI Assessment', type: 'AI_REASON', config: { target: 'invariants' } },
            { id: 'n3', name: 'Generate Output', type: 'OUTPUT', config: { format: 'SUMMARY' } },
          ],
          edges: [
            { source: 'n1', target: 'n2' },
            { source: 'n2', target: 'n3' },
          ],
        }),
      });
      if (res.ok) {
        setIsCreating(false);
        setNewName('');
        setNewDesc('');
        await fetchWorkflows();
      }
    } catch (err) {
      console.error('Failed to create workflow', err);
    }
  };

  return (
    <div className="h-[calc(100vh-3.5rem)] flex flex-col bg-nova-950 font-sans overflow-hidden">
      {/* Header */}
      <div className="h-14 border-b border-nova-800 bg-nova-900/80 px-8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <WorkflowIcon className="h-5 w-5 text-purple-400" />
          <span className="text-sm font-bold text-white">Visual Workflow Pipelines</span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
            DAG Automation Engine
          </span>
        </div>

        <button
          onClick={() => setIsCreating(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs shadow-glow-sm transition-all"
        >
          <Plus className="h-4 w-4" />
          <span>New Workflow</span>
        </button>
      </div>

      {/* Main Container */}
      <div className="flex-1 overflow-y-auto p-8 max-w-6xl mx-auto w-full space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {workflows.map((wf) => (
            <div
              key={wf.id}
              className={`p-6 rounded-2xl border transition-all flex flex-col justify-between space-y-4 ${
                selectedWf?.id === wf.id
                  ? 'bg-nova-900/90 border-purple-500/50 shadow-glow-sm'
                  : 'bg-nova-900/60 border-nova-800 hover:border-nova-700'
              }`}
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-nova-800 text-purple-300 border border-nova-750 uppercase">
                    {wf.trigger_type}
                  </span>
                  <span className="text-xs font-mono text-slate-500">{wf.nodes.length} Nodes</span>
                </div>

                <div>
                  <h3 className="text-sm font-bold text-white">{wf.name}</h3>
                  <p className="text-xs text-slate-400 mt-1 line-clamp-2">{wf.description}</p>
                </div>

                {/* Nodes Preview Sequence */}
                <div className="flex items-center gap-1.5 overflow-x-auto py-2">
                  {wf.nodes.map((node, i) => (
                    <React.Fragment key={node.id}>
                      <span className="px-2.5 py-1 rounded-lg bg-nova-950 border border-nova-850 text-[10px] font-mono text-slate-300 shrink-0">
                        {node.name}
                      </span>
                      {i < wf.nodes.length - 1 && (
                        <ArrowRight className="h-3 w-3 text-slate-600 shrink-0" />
                      )}
                    </React.Fragment>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-between pt-3 border-t border-nova-800/80">
                <span className="text-[10px] font-mono text-emerald-400 flex items-center gap-1">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400"></span> Active
                </span>

                <button
                  onClick={() => handleExecute(wf)}
                  disabled={isRunning}
                  className="flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white text-xs font-bold shadow-glow-sm transition-all"
                >
                  <Play className={`h-3 w-3 ${isRunning && selectedWf?.id === wf.id ? 'animate-spin' : ''}`} />
                  <span>{isRunning && selectedWf?.id === wf.id ? 'Running DAG...' : 'Execute Pipeline'}</span>
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Live Execution Output Trace */}
        {executionResult && (
          <div className="p-6 rounded-2xl bg-nova-900 border border-nova-800 space-y-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-nova-800 pb-3">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                <div>
                  <h3 className="text-sm font-bold text-white">
                    Pipeline Execution Completed: {executionResult.workflow_name}
                  </h3>
                  <span className="text-xs text-slate-400 font-mono">
                    ID: {executionResult.execution_id} • Duration: {executionResult.duration_ms}ms
                  </span>
                </div>
              </div>

              <button
                onClick={() => setExecutionResult(null)}
                className="text-slate-400 hover:text-white"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {/* Traces */}
            <div className="space-y-2">
              {executionResult.traces.map((trace, idx) => (
                <div
                  key={trace.node_id}
                  className="p-3.5 rounded-xl bg-nova-950 border border-nova-850 flex items-start justify-between text-xs font-mono"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-purple-400">Node {idx + 1}:</span>
                      <span className="font-bold text-white">{trace.node_name}</span>
                      <span className="text-[10px] px-1.5 py-0.2 rounded bg-nova-850 text-slate-400">
                        {trace.type}
                      </span>
                    </div>
                    {trace.output && (
                      <div className="text-[11px] text-slate-400 pl-4">{trace.output}</div>
                    )}
                  </div>

                  <div className="flex items-center gap-3 text-[11px]">
                    <span className="text-slate-500">{trace.duration_ms}ms</span>
                    <span className="text-emerald-400 font-bold">{trace.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Modal: Create Workflow */}
      {isCreating && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-nova-900 border border-nova-800 rounded-2xl p-6 w-full max-w-md space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-purple-400" />
              <span>Create Visual Workflow Pipeline</span>
            </h3>

            <div className="space-y-3 text-xs">
              <div>
                <label className="text-slate-400 block mb-1">Pipeline Name</label>
                <input
                  type="text"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="e.g. Daily Tech Radar Digest"
                  className="w-full bg-nova-950 border border-nova-800 rounded-lg p-2 text-white focus:outline-none"
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Description</label>
                <input
                  type="text"
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  placeholder="Objective of this automated DAG pipeline..."
                  className="w-full bg-nova-950 border border-nova-800 rounded-lg p-2 text-white focus:outline-none"
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Trigger Mechanism</label>
                <select
                  value={newTrigger}
                  onChange={(e) => setNewTrigger(e.target.value)}
                  className="w-full bg-nova-950 border border-nova-800 rounded-lg p-2 text-white focus:outline-none"
                >
                  <option value="MANUAL">MANUAL (Dispatch On Demand)</option>
                  <option value="SCHEDULE">SCHEDULE (Cron Schedule)</option>
                  <option value="WEBHOOK">WEBHOOK (HTTP Trigger)</option>
                  <option value="EVENT">EVENT (Workspace File Change)</option>
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
                onClick={handleCreate}
                className="px-4 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs"
              >
                Build Pipeline
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
