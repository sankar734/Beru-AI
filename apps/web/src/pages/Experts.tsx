import React, { useState, useEffect } from 'react';
import {
  BrainCircuit,
  Plus,
  UserCheck,
  Shield,
  Cpu,
  ShieldAlert,
  Zap,
  Brain,
  MessageSquare,
  Sparkles,
  Send,
  Trash2,
  CheckCircle2,
  ArrowRight,
  Sliders,
  X,
} from 'lucide-react';

interface Expert {
  id: string;
  name: string;
  role: string;
  avatar_icon: string;
  color_theme: string;
  system_prompt: string;
  capabilities: string[];
  temperature: number;
  is_system_default: boolean;
}

interface ConsultResult {
  expert_id: string;
  expert_name: string;
  role: string;
  consultation_response: string;
  key_recommendations: string[];
  suggested_followups: string[];
}

export const Experts: React.FC = () => {
  const [experts, setExperts] = useState<Expert[]>([]);
  const [selectedExpert, setSelectedExpert] = useState<Expert | null>(null);
  const [consultQuery, setConsultQuery] = useState<string>('');
  const [consultContext, setConsultContext] = useState<string>('');
  const [isConsulting, setIsConsulting] = useState<boolean>(false);
  const [consultResult, setConsultResult] = useState<ConsultResult | null>(null);

  // New Expert Modal
  const [isCreating, setIsCreating] = useState<boolean>(false);
  const [newName, setNewName] = useState<string>('');
  const [newRole, setNewRole] = useState<string>('');
  const [newPrompt, setNewPrompt] = useState<string>('');
  const [newColor, setNewColor] = useState<string>('purple');
  const [newCapabilities, setNewCapabilities] = useState<string>('Architecture Review, Threat Modeling');

  useEffect(() => {
    fetchExperts();
  }, []);

  const fetchExperts = async () => {
    try {
      const res = await fetch('/api/v1/experts');
      if (res.ok) {
        const data = await res.json();
        setExperts(data);
      }
    } catch (err) {
      console.error('Failed to load experts', err);
    }
  };

  const openConsultation = (exp: Expert) => {
    setSelectedExpert(exp);
    setConsultQuery('');
    setConsultContext('');
    setConsultResult(null);
  };

  const handleConsult = async () => {
    if (!selectedExpert || !consultQuery.trim() || isConsulting) return;
    setIsConsulting(true);
    try {
      const res = await fetch(`/api/v1/experts/${selectedExpert.id}/consult`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: consultQuery, context: consultContext }),
      });
      if (res.ok) {
        const data = await res.json();
        setConsultResult(data);
      }
    } catch (err) {
      console.error('Consultation failed', err);
    } finally {
      setIsConsulting(false);
    }
  };

  const handleCreateExpert = async () => {
    if (!newName.trim() || !newRole.trim() || !newPrompt.trim()) return;
    try {
      const caps = newCapabilities.split(',').map((c) => c.trim()).filter(Boolean);
      const res = await fetch('/api/v1/experts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newName,
          role: newRole,
          system_prompt: newPrompt,
          color_theme: newColor,
          capabilities: caps,
          temperature: 0.3,
        }),
      });
      if (res.ok) {
        setIsCreating(false);
        setNewName('');
        setNewRole('');
        setNewPrompt('');
        await fetchExperts();
      }
    } catch (err) {
      console.error('Failed to create expert', err);
    }
  };

  const getThemeClasses = (color: string) => {
    switch (color) {
      case 'cyan':
        return {
          bg: 'bg-cyan-500/10',
          border: 'border-cyan-500/30',
          text: 'text-cyan-400',
          badge: 'bg-cyan-500/20 text-cyan-300',
        };
      case 'rose':
        return {
          bg: 'bg-rose-500/10',
          border: 'border-rose-500/30',
          text: 'text-rose-400',
          badge: 'bg-rose-500/20 text-rose-300',
        };
      case 'amber':
        return {
          bg: 'bg-amber-500/10',
          border: 'border-amber-500/30',
          text: 'text-amber-400',
          badge: 'bg-amber-500/20 text-amber-300',
        };
      default:
        return {
          bg: 'bg-purple-500/10',
          border: 'border-purple-500/30',
          text: 'text-purple-400',
          badge: 'bg-purple-500/20 text-purple-300',
        };
    }
  };

  const getAvatarIcon = (icon: string) => {
    switch (icon) {
      case 'Cpu':
        return <Cpu className="h-5 w-5" />;
      case 'ShieldAlert':
        return <ShieldAlert className="h-5 w-5" />;
      case 'Zap':
        return <Zap className="h-5 w-5" />;
      default:
        return <Brain className="h-5 w-5" />;
    }
  };

  return (
    <div className="h-[calc(100vh-3.5rem)] flex flex-col bg-nova-950 font-sans overflow-hidden">
      <div className="flex-1 overflow-y-auto p-8 max-w-6xl mx-auto w-full space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-white flex items-center gap-2">
              <BrainCircuit className="h-5 w-5 text-purple-400" />
              <span>Specialized AI Experts & Personas</span>
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Autonomous domain specialists equipped with distinct system directives, architectural mental models, and focused advisory capabilities.
            </p>
          </div>
          <button
            onClick={() => setIsCreating(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs shadow-glow-sm transition-all"
          >
            <Plus className="h-4 w-4" />
            <span>Build Specialist</span>
          </button>
        </div>

        {/* Expert Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {experts.map((exp) => {
            const theme = getThemeClasses(exp.color_theme);
            return (
              <div
                key={exp.id}
                className="p-6 rounded-2xl bg-nova-900/70 border border-nova-800 hover:border-purple-500/40 transition-all flex flex-col justify-between space-y-4 group"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div
                        className={`h-11 w-11 rounded-2xl ${theme.bg} border ${theme.border} ${theme.text} flex items-center justify-center font-bold`}
                      >
                        {getAvatarIcon(exp.avatar_icon)}
                      </div>
                      <div>
                        <h3 className="text-sm font-bold text-white group-hover:text-purple-300 transition-colors">
                          {exp.name}
                        </h3>
                        <p className={`text-xs font-semibold ${theme.text}`}>{exp.role}</p>
                      </div>
                    </div>
                    {exp.is_system_default && (
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-nova-800 text-slate-400">
                        Default
                      </span>
                    )}
                  </div>

                  <p className="text-xs text-slate-400 leading-relaxed line-clamp-3">
                    {exp.system_prompt}
                  </p>

                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {exp.capabilities.map((c, i) => (
                      <span
                        key={i}
                        className={`text-[10px] font-mono px-2 py-0.5 rounded ${theme.badge} border border-transparent`}
                      >
                        {c}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="pt-3 border-t border-nova-800 flex items-center justify-between">
                  <span className="text-[10px] font-mono text-slate-500">
                    Temp: {exp.temperature} • Persona active
                  </span>
                  <button
                    onClick={() => openConsultation(exp)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-nova-850 hover:bg-nova-800 text-white text-xs font-semibold border border-nova-750 transition-colors"
                  >
                    <MessageSquare className="h-3.5 w-3.5 text-purple-400" />
                    <span>Consult Specialist</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Consultation Modal / Drawer */}
      {selectedExpert && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-nova-900 border border-nova-800 rounded-2xl p-6 w-full max-w-2xl max-h-[85vh] flex flex-col space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-nova-800 pb-3">
              <div className="flex items-center gap-3">
                <div className="h-9 w-9 rounded-xl bg-purple-500/20 text-purple-300 flex items-center justify-center font-bold">
                  {getAvatarIcon(selectedExpert.avatar_icon)}
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white">{selectedExpert.name}</h3>
                  <p className="text-xs text-purple-400">{selectedExpert.role}</p>
                </div>
              </div>
              <button
                onClick={() => setSelectedExpert(null)}
                className="text-slate-400 hover:text-white"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto space-y-4 text-xs">
              {!consultResult ? (
                <div className="space-y-3">
                  <div>
                    <label className="text-slate-400 block mb-1">
                      Problem Statement / Architectural Dilemma
                    </label>
                    <textarea
                      rows={3}
                      value={consultQuery}
                      onChange={(e) => setConsultQuery(e.target.value)}
                      placeholder="e.g. How do we achieve sub-millisecond tail latency while guaranteeing linearizable distributed transactions?"
                      className="w-full bg-nova-950 border border-nova-800 rounded-xl p-3 text-white focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400 block mb-1">
                      Relevant Technical Context (Optional)
                    </label>
                    <textarea
                      rows={2}
                      value={consultContext}
                      onChange={(e) => setConsultContext(e.target.value)}
                      placeholder="e.g. Tech stack: Python 3.14, FastAPI, Raft, MongoDB, Redis, WebSockets..."
                      className="w-full bg-nova-950 border border-nova-800 rounded-xl p-3 text-white focus:outline-none"
                    />
                  </div>
                  <div className="flex justify-end pt-2">
                    <button
                      onClick={handleConsult}
                      disabled={isConsulting || !consultQuery.trim()}
                      className="flex items-center gap-2 px-5 py-2 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white font-bold text-xs rounded-xl shadow-glow-sm"
                    >
                      <Sparkles className="h-3.5 w-3.5" />
                      <span>{isConsulting ? 'Formulating Strategy...' : 'Request Consultation'}</span>
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="p-4 rounded-xl bg-nova-950 border border-nova-850 space-y-3">
                    <span className="text-xs font-bold text-purple-300 font-mono">
                      Specialist Recommendation & Analysis
                    </span>
                    <div className="text-slate-200 whitespace-pre-wrap leading-relaxed">
                      {consultResult.consultation_response}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <span className="text-[11px] font-bold text-slate-400 font-mono uppercase tracking-wider">
                      Key Recommendations
                    </span>
                    <div className="space-y-1.5">
                      {consultResult.key_recommendations.map((rec, i) => (
                        <div
                          key={i}
                          className="flex items-start gap-2 p-2 rounded-lg bg-nova-950 border border-nova-850 text-emerald-300 text-xs"
                        >
                          <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400 mt-0.5" />
                          <span>{rec}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="flex justify-between items-center pt-2 border-t border-nova-800">
                    <button
                      onClick={() => setConsultResult(null)}
                      className="text-xs text-purple-400 hover:underline"
                    >
                      &larr; Ask Another Question
                    </button>
                    <button
                      onClick={() => setSelectedExpert(null)}
                      className="px-4 py-1.5 bg-nova-800 hover:bg-nova-750 text-white text-xs rounded-lg"
                    >
                      Done
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Modal: Create Custom Expert */}
      {isCreating && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-nova-900 border border-nova-800 rounded-2xl p-6 w-full max-w-lg space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-purple-400" />
              <span>Configure Custom Specialist Persona</span>
            </h3>

            <div className="space-y-3 text-xs">
              <div>
                <label className="text-slate-400 block mb-1">Expert Name</label>
                <input
                  type="text"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="e.g. Siobhan Roy"
                  className="w-full bg-nova-950 border border-nova-800 rounded-lg p-2 text-white focus:outline-none"
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Professional Role</label>
                <input
                  type="text"
                  value={newRole}
                  onChange={(e) => setNewRole(e.target.value)}
                  placeholder="e.g. Chief Product & Monetization Strategist"
                  className="w-full bg-nova-950 border border-nova-800 rounded-lg p-2 text-white focus:outline-none"
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">System Directive Prompt</label>
                <textarea
                  rows={3}
                  value={newPrompt}
                  onChange={(e) => setNewPrompt(e.target.value)}
                  placeholder="Define persona background, mental models, axioms, and communication tone..."
                  className="w-full bg-nova-950 border border-nova-800 rounded-lg p-2 text-white focus:outline-none"
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Capabilities (Comma-separated)</label>
                <input
                  type="text"
                  value={newCapabilities}
                  onChange={(e) => setNewCapabilities(e.target.value)}
                  placeholder="e.g. Pricing Models, Moat Analysis, Enterprise Roadmaps"
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
                onClick={handleCreateExpert}
                className="px-4 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs"
              >
                Save Expert
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
