import React, { useEffect, useState, useRef } from 'react';
import { 
  FileText, 
  Upload, 
  Trash2, 
  Search, 
  Sparkles, 
  Database, 
  Layers, 
  CheckCircle2, 
  FileCode, 
  AlertCircle 
} from 'lucide-react';

interface FileRecord {
  id: string;
  file_name: string;
  file_size: number;
  mime_type: string;
  chunk_count: number;
  created_at: string;
}

interface GroundedChunk {
  chunk_id: string;
  file_id: string;
  file_name: string;
  page_number: number;
  section_title: string;
  text: string;
  score: number;
}

interface RAGResponse {
  query: string;
  answer: string;
  grounded_chunks: GroundedChunk[];
}

export const Files: React.FC = () => {
  const [files, setFiles] = useState<FileRecord[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [isQuerying, setIsQuerying] = useState(false);
  const [ragResult, setRagResult] = useState<RAGResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchFiles = async () => {
    const token = localStorage.getItem('nova_token');
    try {
      const res = await fetch('/api/v1/files', {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) {
        const data = await res.json();
        setFiles(data);
      }
    } catch {}
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    setIsUploading(true);
    setError(null);
    const token = localStorage.getItem('nova_token');

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const res = await fetch('/api/v1/files/upload', {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: formData,
      });
      if (res.ok) {
        await fetchFiles();
      } else {
        const err = await res.json();
        setError(err.detail || 'Upload failed');
      }
    } catch {
      setError('Network error during upload');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleDelete = async (id: string) => {
    const token = localStorage.getItem('nova_token');
    try {
      const res = await fetch(`/api/v1/files/${id}`, {
        method: 'DELETE',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) {
        setFiles(files.filter((f) => f.id !== id));
      }
    } catch {}
  };

  const handleRAGQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim() || isQuerying) return;

    setIsQuerying(true);
    setRagResult(null);
    const token = localStorage.getItem('nova_token');

    try {
      const res = await fetch('/api/v1/files/rag/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ query: searchQuery, top_k: 5 }),
      });
      if (res.ok) {
        const data = await res.json();
        setRagResult(data);
      }
    } catch {}
    finally {
      setIsQuerying(false);
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 font-sans animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl font-extrabold text-white flex items-center gap-2.5">
            <FileText className="h-6 w-6 text-nova-cyan" />
            <span>Files & Hybrid RAG Intelligence</span>
          </h1>
          <p className="text-xs text-slate-400">
            Multi-format document ingestion, semantic sliding-window chunking, dense + BM25 hybrid retrieval, and grounded citations.
          </p>
        </div>

        <div>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            className="hidden"
            accept=".pdf,.docx,.txt,.md,.json,.csv,.py,.ts"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-nova-accent to-blue-600 hover:from-blue-600 hover:to-nova-accent text-white font-semibold text-xs shadow-glow-sm disabled:opacity-50 transition-all cursor-pointer"
          >
            <Upload className="h-4 w-4" />
            <span>{isUploading ? 'Chunking & Indexing...' : 'Upload Document'}</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center gap-2 text-xs text-rose-400">
          <AlertCircle className="h-4 w-4" />
          <span>{error}</span>
        </div>
      )}

      {/* "Ask My Documents" Hybrid RAG Query Box */}
      <div className="glass-panel-elevated p-4 rounded-2xl border border-nova-750 shadow-xl space-y-3">
        <div className="flex items-center justify-between text-xs font-mono text-slate-400 px-1">
          <span className="flex items-center gap-1.5 font-bold uppercase tracking-wider text-slate-200">
            <Sparkles className="h-3.5 w-3.5 text-nova-accent" />
            <span>Ask My Documents (Hybrid Dense + BM25 Search)</span>
          </span>
          <span className="text-[10px] text-nova-cyan bg-nova-cyan/10 px-2 py-0.5 rounded border border-nova-cyan/20">
            RECIPROCAL RANK FUSION
          </span>
        </div>

        <form onSubmit={handleRAGQuery} className="flex items-center gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="e.g., What is our zero-trust permission security model?"
            className="w-full bg-nova-900 border border-nova-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-nova-accent"
          />
          <button
            type="submit"
            disabled={isQuerying || !searchQuery.trim()}
            className="px-5 py-2.5 bg-nova-850 hover:bg-nova-800 border border-nova-750 text-white rounded-xl text-xs font-semibold shrink-0 disabled:opacity-40 transition-colors"
          >
            {isQuerying ? 'Retrieving...' : 'Query RAG'}
          </button>
        </form>

        {/* Grounded RAG Response */}
        {ragResult && (
          <div className="p-4 rounded-xl bg-nova-900/80 border border-nova-800 space-y-3 animate-in fade-in">
            <div className="text-xs text-slate-200 leading-relaxed whitespace-pre-wrap">
              {ragResult.answer}
            </div>

            {/* Grounded Chunks */}
            <div className="pt-2 border-t border-nova-800/80 space-y-2">
              <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 block font-semibold">
                Retrieved Grounded Passages ({ragResult.grounded_chunks.length})
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {ragResult.grounded_chunks.map((chunk, idx) => (
                  <div
                    key={chunk.chunk_id || idx}
                    className="p-2.5 rounded-lg bg-nova-950/60 border border-nova-800 text-[11px] space-y-1"
                  >
                    <div className="flex items-center justify-between text-slate-300 font-semibold">
                      <span className="truncate">[{idx + 1}] {chunk.file_name}</span>
                      <span className="text-[10px] font-mono text-nova-cyan shrink-0">Page {chunk.page_number}</span>
                    </div>
                    <div className="text-[10px] font-mono text-slate-500">Section: {chunk.section_title}</div>
                    <p className="text-slate-400 line-clamp-3 leading-relaxed text-[10px]">{chunk.text}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Uploaded Documents List */}
      <div className="glass-panel p-6 rounded-2xl border border-nova-750 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
            <Database className="h-4 w-4 text-nova-accent" />
            <span>Indexed Documents ({files.length})</span>
          </h2>
          <span className="text-[11px] text-slate-500 font-mono">Vector Storage: Active</span>
        </div>

        {files.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-500 space-y-2">
            <FileText className="h-8 w-8 text-slate-600 mx-auto" />
            <p>No documents uploaded yet. Upload a PDF, DOCX, Markdown, or code file to start.</p>
          </div>
        ) : (
          <div className="divide-y divide-nova-800/80">
            {files.map((file) => (
              <div key={file.id} className="py-3 flex items-center justify-between text-xs">
                <div className="flex items-center gap-3 min-w-0 pr-4">
                  <div className="h-8 w-8 rounded-lg bg-nova-850 border border-nova-800 flex items-center justify-center text-nova-cyan shrink-0">
                    <FileCode className="h-4 w-4" />
                  </div>
                  <div className="min-w-0">
                    <div className="font-semibold text-slate-200 truncate">{file.file_name}</div>
                    <div className="text-[10px] text-slate-500 flex items-center gap-2 font-mono">
                      <span>{(file.file_size / 1024).toFixed(1)} KB</span>
                      <span>•</span>
                      <span>{file.chunk_count} Chunks Indexed</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                    INDEXED
                  </span>
                  <button
                    onClick={() => handleDelete(file.id)}
                    className="p-1.5 text-slate-500 hover:text-rose-400 hover:bg-nova-850 rounded-lg transition-colors"
                    title="Delete Document & Chunks"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
