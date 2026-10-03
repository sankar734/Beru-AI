import React, { useEffect, useState } from 'react';
import { 
  Compass, 
  Sparkles, 
  Layers, 
  CheckCircle2, 
  Clock, 
  AlertTriangle, 
  FileText, 
  ExternalLink, 
  ShieldCheck, 
  XOctagon, 
  BookOpen, 
  TrendingUp 
} from 'lucide-react';

interface SubQuestion {
  id: string;
  question: string;
  status: string;
  findings_count: number;
}

interface EvidenceItem {
  id: string;
  subquestion_id: string;
  source_title: string;
  source_url: string;
  claim: string;
  is_contradiction: boolean;
  confidence: number;
}

interface ResearchJob {
  id: string;
  goal: string;
  status: string;
  progress: number;
  subquestions: SubQuestion[];
  evidence: EvidenceItem[];
  sources: Array<{ title: string; url: string }>;
  final_report?: string;
  created_at: string;
}

export const Research: React.FC = () => {
  const [goal, setGoal] = useState('');
  const [depth, setDepth] = useState('comprehensive');
  const [activeJob, setActiveJob] = useState<ResearchJob | null>(null);
  const [jobsHistory, setJobsHistory] = useState<ResearchJob[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'report' | 'evidence' | 'subquestions'>('report');

  const fetchJobs = async () => {
    const token = localStorage.getItem('nova_token');
    try {
      const res = await fetch('/api/v1/research/jobs', {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) {
        const data = await res.json();
        setJobsHistory(data);
        if (data.length > 0 && !activeJob) {
          setActiveJob(data[0]);
        }
      }
    } catch {}
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const handleLaunch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!goal.trim() || isLoading) return;

    setIsLoading(true);
    const token = localStorage.getItem('nova_token');

    try {
      const res = await fetch('/api/v1/research/jobs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ goal, depth }),
      });
      if (res.ok) {
        const data = await res.json();
        setActiveJob(data);
        fetchJobs();
        setGoal('');
      }
    } catch {}
    finally {
      setIsLoading(false);
    }
  };

  const handleCancel = async () => {
    if (!activeJob) return;
    const token = localStorage.getItem('nova_token');
    try {
      const res = await fetch(`/api/v1/research/jobs/${activeJob.id}/cancel`, {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) {
        const data = await res.json();
        setActiveJob(data);
        fetchJobs();
      }
    } catch {}
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 font-sans animate-in fade-in duration-200">
      {/* Header */}
      <div className="space-y-1">
        <h1 className="text-2xl font-extrabold text-white flex items-center gap-2.5">
          <Compass className="h-6 w-6 text-blue-400" />
          <span>Deep Research System</span>
        </h1>
        <p className="text-xs text-slate-400">
          Autonomous multi-agent research jobs synthesizing exhaustive, fact-checked reports with contradiction detection and citation audits.
        </p>
      </div>

      {/* Launcher Card */}
      <div className="glass-panel-elevated p-6 rounded-2xl border border-nova-750 shadow-2xl space-y-4">
        <form onSubmit={handleLaunch} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">Research Goal or Thesis</label>
            <textarea
              rows={3}
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              placeholder="e.g., Investigate state-of-the-art hybrid RAG architectures with cross-encoder reranking and compare performance against pure vector retrieval..."
              className="w-full bg-nova-900 border border-nova-800 rounded-xl p-3.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-400 resize-none"
            />
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1 border-t border-nova-800/80">
            <div className="flex items-center gap-2">
              <span className="text-[11px] text-slate-400 font-medium">Depth:</span>
              <select
                value={depth}
                onChange={(e) => setDepth(e.target.value)}
                className="bg-nova-900 border border-nova-800 rounded-lg px-2.5 py-1 text-xs text-slate-200 focus:outline-none font-mono"
              >
                <option value="quick">Quick (1-2 Sources)</option>
                <option value="standard">Standard (3-5 Sources)</option>
                <option value="comprehensive">Comprehensive (Multi-source + Skeptic)</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={isLoading || !goal.trim()}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-semibold text-xs shadow-glow-sm disabled:opacity-50 transition-all flex items-center justify-center gap-2"
            >
              <Compass className="h-4 w-4" />
              <span>{isLoading ? 'Synthesizing...' : 'Launch Deep Research'}</span>
            </button>
          </div>
        </form>
      </div>

      {/* Active Job Progress & Details */}
      {activeJob && (
        <div className="space-y-6">
          {/* Progress Bar & Status */}
          <div className="glass-panel p-6 rounded-2xl border border-nova-750 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-[10px] font-mono text-blue-400 uppercase tracking-widest block font-semibold">
                  Active Investigation
                </span>
                <h2 className="text-base font-bold text-white mt-0.5">{activeJob.goal}</h2>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">
                  {activeJob.status} ({activeJob.progress}%)
                </span>
                {activeJob.status !== 'COMPLETED' && activeJob.status !== 'CANCELLED' && (
                  <button
                    onClick={handleCancel}
                    className="p-1 text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                    title="Cancel Job"
                  >
                    <XOctagon className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>

            <div className="w-full bg-nova-900 rounded-full h-2 overflow-hidden border border-nova-800">
              <div
                className="bg-gradient-to-r from-blue-500 to-indigo-500 h-full rounded-full transition-all duration-500"
                style={{ width: `${activeJob.progress}%` }}
              />
            </div>

            {/* Sub-steps */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 text-[11px] font-mono text-slate-400">
              <div className="flex items-center gap-1.5 text-emerald-400">
                <CheckCircle2 className="h-3.5 w-3.5" />
                <span>1. Deconstruct Goal</span>
              </div>
              <div className="flex items-center gap-1.5 text-emerald-400">
                <CheckCircle2 className="h-3.5 w-3.5" />
                <span>2. Multi-Source Search</span>
              </div>
              <div className="flex items-center gap-1.5 text-emerald-400">
                <CheckCircle2 className="h-3.5 w-3.5" />
                <span>3. Skeptic Check</span>
              </div>
              <div className="flex items-center gap-1.5 text-emerald-400">
                <CheckCircle2 className="h-3.5 w-3.5" />
                <span>4. Verified Synthesis</span>
              </div>
            </div>
          </div>

          {/* View Tabs */}
          <div className="flex items-center gap-2 border-b border-nova-800 pb-2">
            <button
              onClick={() => setActiveTab('report')}
              className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                activeTab === 'report' ? 'bg-nova-800 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Synthesized Report
            </button>
            <button
              onClick={() => setActiveTab('evidence')}
              className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                activeTab === 'evidence' ? 'bg-nova-800 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Evidence Graph ({activeJob.evidence.length})
            </button>
            <button
              onClick={() => setActiveTab('subquestions')}
              className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                activeTab === 'subquestions' ? 'bg-nova-800 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Subquestions ({activeJob.subquestions.length})
            </button>
          </div>

          {/* Tab Content: Report */}
          {activeTab === 'report' && (
            <div className="glass-panel-elevated p-8 rounded-2xl border border-nova-750 shadow-xl space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-nova-800">
                <div className="flex items-center gap-2 text-xs font-mono text-emerald-400">
                  <ShieldCheck className="h-4 w-4" />
                  <span>Exhaustive Synthesis Verified</span>
                </div>
                <span className="text-[11px] text-slate-500 font-mono">Job ID: {activeJob.id.slice(0, 8)}</span>
              </div>

              <div className="text-xs text-slate-200 leading-relaxed whitespace-pre-wrap font-sans space-y-2">
                {activeJob.final_report || 'Synthesizing report...'}
              </div>
            </div>
          )}

          {/* Tab Content: Evidence Graph */}
          {activeTab === 'evidence' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {activeJob.evidence.map((ev) => (
                <div
                  key={ev.id}
                  className={`p-4 rounded-xl glass-panel border space-y-2 ${
                    ev.is_contradiction
                      ? 'border-amber-500/30 bg-amber-500/5'
                      : 'border-nova-800'
                  }`}
                >
                  <div className="flex items-center justify-between text-[11px] font-mono">
                    <span className="text-slate-400 truncate pr-2">{ev.source_title}</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] ${
                      ev.is_contradiction
                        ? 'text-amber-400 bg-amber-500/10 border border-amber-500/20'
                        : 'text-emerald-400 bg-emerald-500/10 border border-emerald-500/20'
                    }`}>
                      {ev.is_contradiction ? 'CONTRADICTION' : 'CORROBORATED'}
                    </span>
                  </div>
                  <p className="text-xs text-slate-200 leading-relaxed font-sans">{ev.claim}</p>
                  <div className="text-[10px] text-slate-500 font-mono">
                    Confidence: {Math.round(ev.confidence * 100)}%
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Tab Content: Subquestions */}
          {activeTab === 'subquestions' && (
            <div className="space-y-2">
              {activeJob.subquestions.map((sq, i) => (
                <div
                  key={sq.id}
                  className="p-3.5 rounded-xl glass-panel border border-nova-800 flex items-center justify-between text-xs"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-slate-500 font-mono">0{i + 1}</span>
                    <span className="font-semibold text-slate-200">{sq.question}</span>
                  </div>
                  <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">
                    {sq.findings_count} Findings
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
