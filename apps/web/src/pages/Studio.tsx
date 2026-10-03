import React, { useState, useEffect } from 'react';
import {
  Paintbrush,
  FileText,
  Code2,
  Layout,
  Presentation,
  Plus,
  Eye,
  GitBranch,
  Save,
  Trash2,
  Clock,
  Sparkles,
  ArrowLeft,
  Check,
  Split,
  FileCode,
} from 'lucide-react';

interface ArtifactVersion {
  version: number;
  content: string;
  summary: string;
  created_at: string;
}

interface Artifact {
  id: string;
  user_id: string;
  title: string;
  type: string;
  description: string;
  tags: string[];
  current_version: number;
  versions: ArtifactVersion[];
  created_at: string;
  updated_at: string;
}

export const Studio: React.FC = () => {
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [selectedArtifact, setSelectedArtifact] = useState<Artifact | null>(null);
  const [activeVersionNum, setActiveVersionNum] = useState<number>(1);
  const [editorContent, setEditorContent] = useState<string>('');
  const [filterType, setFilterType] = useState<string>('ALL');
  const [isSavingVersion, setIsSavingVersion] = useState<boolean>(false);
  const [versionSummary, setVersionSummary] = useState<string>('');
  const [isCreating, setIsCreating] = useState<boolean>(false);
  const [newTitle, setNewTitle] = useState<string>('');
  const [newType, setNewType] = useState<string>('DOCUMENT');
  const [newDesc, setNewDesc] = useState<string>('');
  const [newContent, setNewContent] = useState<string>('');
  const [viewMode, setViewMode] = useState<'split' | 'code' | 'preview'>('split');
  const [diffData, setDiffData] = useState<{ v1: number; v2: number; lines: string[] } | null>(null);
  const [showDiff, setShowDiff] = useState<boolean>(false);

  useEffect(() => {
    fetchArtifacts();
  }, []);

  const fetchArtifacts = async () => {
    try {
      const res = await fetch('/api/v1/artifacts');
      if (res.ok) {
        const data = await res.json();
        setArtifacts(data);
      }
    } catch (err) {
      console.error('Failed to fetch artifacts', err);
    }
  };

  const openArtifact = (art: Artifact) => {
    setSelectedArtifact(art);
    setActiveVersionNum(art.current_version);
    const currV = art.versions.find((v) => v.version === art.current_version);
    setEditorContent(currV ? currV.content : '');
    setShowDiff(false);
  };

  const handleSelectVersion = (vNum: number) => {
    if (!selectedArtifact) return;
    setActiveVersionNum(vNum);
    const targetV = selectedArtifact.versions.find((v) => v.version === vNum);
    if (targetV) {
      setEditorContent(targetV.content);
    }
  };

  const handleSaveNewVersion = async () => {
    if (!selectedArtifact || isSavingVersion) return;
    setIsSavingVersion(true);
    try {
      const res = await fetch(`/api/v1/artifacts/${selectedArtifact.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          new_content: editorContent,
          version_summary: versionSummary.trim() || `Version ${selectedArtifact.versions.length + 1}`,
        }),
      });
      if (res.ok) {
        const updated = await res.json();
        setSelectedArtifact(updated);
        setActiveVersionNum(updated.current_version);
        setVersionSummary('');
        fetchArtifacts();
      }
    } catch (err) {
      console.error('Failed to save artifact version', err);
    } finally {
      setIsSavingVersion(false);
    }
  };

  const handleCreateArtifact = async () => {
    if (!newTitle.trim()) return;
    try {
      const res = await fetch('/api/v1/artifacts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: newTitle,
          type: newType,
          description: newDesc,
          initial_content: newContent || '# New Artifact Content\n',
          tags: [newType.toLowerCase()],
        }),
      });
      if (res.ok) {
        const created = await res.json();
        setIsCreating(false);
        setNewTitle('');
        setNewDesc('');
        setNewContent('');
        await fetchArtifacts();
        openArtifact(created);
      }
    } catch (err) {
      console.error('Failed to create artifact', err);
    }
  };

  const handleViewDiff = async () => {
    if (!selectedArtifact || selectedArtifact.versions.length < 2) return;
    const v2 = selectedArtifact.current_version;
    const v1 = v2 - 1;
    try {
      const res = await fetch(`/api/v1/artifacts/${selectedArtifact.id}/diff?v1=${v1}&v2=${v2}`);
      if (res.ok) {
        const data = await res.json();
        setDiffData({ v1, v2, lines: data.diff_lines });
        setShowDiff(true);
      }
    } catch (err) {
      console.error('Failed to load diff', err);
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type.toUpperCase()) {
      case 'WEB_APP':
        return <Code2 className="h-5 w-5 text-blue-400" />;
      case 'DOCUMENT':
        return <FileText className="h-5 w-5 text-purple-400" />;
      case 'DIAGRAM':
        return <Layout className="h-5 w-5 text-amber-400" />;
      case 'REPORT':
        return <FileCode className="h-5 w-5 text-emerald-400" />;
      default:
        return <Presentation className="h-5 w-5 text-rose-400" />;
    }
  };

  const filteredArtifacts =
    filterType === 'ALL'
      ? artifacts
      : artifacts.filter((a) => a.type.toUpperCase() === filterType);

  return (
    <div className="h-[calc(100vh-3.5rem)] flex flex-col bg-nova-950 overflow-hidden font-sans">
      {!selectedArtifact ? (
        /* Artifacts Gallery / Dashboard */
        <div className="flex-1 overflow-y-auto p-8 max-w-6xl mx-auto w-full space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-white flex items-center gap-2">
                <Paintbrush className="h-5 w-5 text-purple-400" />
                <span>NOVA Studio Artifacts</span>
              </h1>
              <p className="text-xs text-slate-400 mt-1">
                Persistent engineering and creative workspaces: Web Apps, interactive documents, diagrams, and reports with continuous version snapshotting.
              </p>
            </div>
            <button
              onClick={() => setIsCreating(true)}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs shadow-glow-sm transition-all"
            >
              <Plus className="h-4 w-4" />
              <span>New Artifact</span>
            </button>
          </div>

          {/* Type Filters */}
          <div className="flex items-center gap-2 border-b border-nova-800 pb-3">
            {['ALL', 'WEB_APP', 'DOCUMENT', 'DIAGRAM', 'REPORT'].map((t) => (
              <button
                key={t}
                onClick={() => setFilterType(t)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                  filterType === t
                    ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-nova-900'
                }`}
              >
                {t}
              </button>
            ))}
          </div>

          {/* Artifact Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredArtifacts.map((art) => (
              <div
                key={art.id}
                onClick={() => openArtifact(art)}
                className="p-5 rounded-xl bg-nova-900/70 border border-nova-800 hover:border-purple-500/50 hover:bg-nova-850/80 cursor-pointer transition-all space-y-3 group"
              >
                <div className="flex items-center justify-between">
                  <div className="p-2 rounded-lg bg-nova-800 group-hover:bg-purple-500/10 transition-colors">
                    {getTypeIcon(art.type)}
                  </div>
                  <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-nova-800 text-purple-300 border border-nova-750">
                    v{art.current_version}
                  </span>
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white group-hover:text-purple-300 transition-colors">
                    {art.title}
                  </h3>
                  <p className="text-xs text-slate-400 line-clamp-2 mt-1">
                    {art.description || 'No description provided'}
                  </p>
                </div>
                <div className="flex items-center justify-between text-[11px] text-slate-500 pt-2 border-t border-nova-800/80">
                  <span className="font-mono text-[10px] uppercase text-slate-400">
                    {art.type}
                  </span>
                  <span>{new Date(art.updated_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Creation Modal */}
          {isCreating && (
            <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
              <div className="bg-nova-900 border border-nova-800 rounded-2xl p-6 w-full max-w-lg space-y-4 shadow-2xl">
                <h2 className="text-sm font-bold text-white flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-purple-400" />
                  <span>Create New Artifact</span>
                </h2>
                <div className="space-y-3 text-xs">
                  <div>
                    <label className="text-slate-400 block mb-1">Title</label>
                    <input
                      type="text"
                      value={newTitle}
                      onChange={(e) => setNewTitle(e.target.value)}
                      placeholder="e.g. Sales Funnel Visualizer"
                      className="w-full bg-nova-950 border border-nova-800 rounded-lg p-2 text-white focus:outline-none focus:border-purple-500"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400 block mb-1">Artifact Type</label>
                    <select
                      value={newType}
                      onChange={(e) => setNewType(e.target.value)}
                      className="w-full bg-nova-950 border border-nova-800 rounded-lg p-2 text-white focus:outline-none"
                    >
                      <option value="WEB_APP">WEB_APP (HTML/CSS/JS Canvas)</option>
                      <option value="DOCUMENT">DOCUMENT (Markdown Article)</option>
                      <option value="DIAGRAM">DIAGRAM (Mermaid Flowchart)</option>
                      <option value="REPORT">REPORT (Analytical Findings)</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-slate-400 block mb-1">Description</label>
                    <input
                      type="text"
                      value={newDesc}
                      onChange={(e) => setNewDesc(e.target.value)}
                      placeholder="Brief purpose of this artifact..."
                      className="w-full bg-nova-950 border border-nova-800 rounded-lg p-2 text-white focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400 block mb-1">Initial Content</label>
                    <textarea
                      rows={5}
                      value={newContent}
                      onChange={(e) => setNewContent(e.target.value)}
                      placeholder="Initial code, markdown or markup..."
                      className="w-full bg-nova-950 border border-nova-800 rounded-lg p-2 text-white font-mono focus:outline-none resize-none"
                    />
                  </div>
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <button
                    onClick={() => setIsCreating(false)}
                    className="px-3 py-1.5 rounded-lg bg-nova-800 text-slate-300 text-xs hover:bg-nova-750"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleCreateArtifact}
                    className="px-4 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold"
                  >
                    Create Artifact
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Active Artifact Studio Workbench */
        <div className="flex-1 flex flex-col min-w-0">
          {/* Header Bar */}
          <div className="h-12 border-b border-nova-800 bg-nova-900/90 px-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setSelectedArtifact(null)}
                className="p-1.5 rounded-lg bg-nova-850 hover:bg-nova-800 text-slate-400 hover:text-white transition-colors"
                title="Back to gallery"
              >
                <ArrowLeft className="h-4 w-4" />
              </button>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-white">{selectedArtifact.title}</span>
                  <span className="text-[10px] font-mono px-2 py-0.2 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
                    {selectedArtifact.type}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* Version Selector */}
              <div className="flex items-center gap-1.5 text-xs text-slate-300">
                <Clock className="h-3.5 w-3.5 text-slate-400" />
                <select
                  value={activeVersionNum}
                  onChange={(e) => handleSelectVersion(Number(e.target.value))}
                  className="bg-nova-850 border border-nova-800 rounded px-2 py-1 text-xs text-white focus:outline-none"
                >
                  {selectedArtifact.versions.map((v) => (
                    <option key={v.version} value={v.version}>
                      v{v.version} - {v.summary}
                    </option>
                  ))}
                </select>
              </div>

              {selectedArtifact.versions.length > 1 && (
                <button
                  onClick={handleViewDiff}
                  className="flex items-center gap-1 px-2.5 py-1 rounded bg-nova-850 hover:bg-nova-800 text-slate-300 text-xs border border-nova-800 transition-colors"
                >
                  <GitBranch className="h-3 w-3 text-purple-400" />
                  <span>Diff</span>
                </button>
              )}

              {/* View Mode Switcher */}
              <div className="flex items-center rounded-lg bg-nova-850 p-0.5 border border-nova-800">
                <button
                  onClick={() => setViewMode('split')}
                  className={`px-2 py-1 text-xs rounded transition-colors ${
                    viewMode === 'split' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <Split className="h-3 w-3" />
                </button>
                <button
                  onClick={() => setViewMode('code')}
                  className={`px-2 py-1 text-xs rounded transition-colors ${
                    viewMode === 'code' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <Code2 className="h-3 w-3" />
                </button>
                <button
                  onClick={() => setViewMode('preview')}
                  className={`px-2 py-1 text-xs rounded transition-colors ${
                    viewMode === 'preview' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <Eye className="h-3 w-3" />
                </button>
              </div>

              {/* Save New Version Button */}
              <button
                onClick={handleSaveNewVersion}
                disabled={isSavingVersion}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-purple-600 hover:bg-purple-500 text-white rounded-lg text-xs font-semibold shadow-glow-sm transition-all"
              >
                <Save className="h-3.5 w-3.5" />
                <span>{isSavingVersion ? 'Saving...' : 'New Snapshot'}</span>
              </button>
            </div>
          </div>

          {/* Workbench Body */}
          <div className="flex-1 flex overflow-hidden">
            {/* Left: Code / Markdown Editor */}
            {(viewMode === 'split' || viewMode === 'code') && (
              <div className={`${viewMode === 'split' ? 'w-1/2' : 'w-full'} flex flex-col border-r border-nova-800 bg-nova-950`}>
                <div className="h-8 border-b border-nova-850 bg-nova-900/60 px-3 flex items-center justify-between text-[11px] font-mono text-slate-400">
                  <span>Source Editor (v{activeVersionNum})</span>
                  <span>{editorContent.length} chars</span>
                </div>
                <textarea
                  value={editorContent}
                  onChange={(e) => setEditorContent(e.target.value)}
                  className="flex-1 bg-transparent p-4 font-mono text-xs text-slate-100 placeholder-slate-600 focus:outline-none resize-none leading-relaxed"
                  placeholder="Artifact payload..."
                />
              </div>
            )}

            {/* Right: Live Preview Panel */}
            {(viewMode === 'split' || viewMode === 'preview') && (
              <div className={`${viewMode === 'split' ? 'w-1/2' : 'w-full'} flex flex-col bg-nova-900/40`}>
                <div className="h-8 border-b border-nova-850 bg-nova-900/60 px-3 flex items-center justify-between text-[11px] font-mono text-slate-400">
                  <span>Live Render Preview</span>
                  <span className="text-emerald-400 flex items-center gap-1">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-400"></span> Live
                  </span>
                </div>

                <div className="flex-1 p-4 overflow-auto">
                  {selectedArtifact.type === 'WEB_APP' ? (
                    <iframe
                      srcDoc={editorContent}
                      title="Web App Preview"
                      sandbox="allow-scripts"
                      className="w-full h-full min-h-[400px] border border-nova-800 rounded-xl bg-white/5"
                    />
                  ) : (
                    <div className="prose prose-invert max-w-none text-xs text-slate-200 whitespace-pre-wrap font-sans leading-relaxed bg-nova-900/50 p-4 rounded-xl border border-nova-800">
                      {editorContent}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Diff Modal */}
          {showDiff && diffData && (
            <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-6">
              <div className="bg-nova-900 border border-nova-800 rounded-2xl p-6 w-full max-w-3xl max-h-[80vh] flex flex-col space-y-3">
                <div className="flex items-center justify-between border-b border-nova-800 pb-2">
                  <h3 className="text-xs font-bold text-white flex items-center gap-2">
                    <GitBranch className="h-4 w-4 text-purple-400" />
                    <span>Version Comparison: v{diffData.v1} &rarr; v{diffData.v2}</span>
                  </h3>
                  <button
                    onClick={() => setShowDiff(false)}
                    className="text-xs text-slate-400 hover:text-white"
                  >
                    Close
                  </button>
                </div>
                <div className="flex-1 overflow-y-auto bg-nova-950 p-3 rounded-xl border border-nova-800 font-mono text-xs space-y-0.5">
                  {diffData.lines.length === 0 ? (
                    <p className="text-slate-500 italic">No textual differences found between versions.</p>
                  ) : (
                    diffData.lines.map((l, i) => (
                      <div
                        key={i}
                        className={
                          l.startsWith('+')
                            ? 'text-emerald-400 bg-emerald-500/10 px-1'
                            : l.startsWith('-')
                            ? 'text-rose-400 bg-rose-500/10 px-1'
                            : 'text-slate-400'
                        }
                      >
                        {l}
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
