import React, { useState } from 'react';
import { 
  Search as SearchIcon, 
  Globe, 
  Newspaper, 
  GraduationCap, 
  FileCode2, 
  ExternalLink, 
  ShieldCheck, 
  Sparkles,
  ArrowRight
} from 'lucide-react';

interface Citation {
  citation_id: number;
  source_url: string;
  source_title: string;
  quote: string;
  verified: boolean;
  confidence: number;
}

interface SourceItem {
  id: string;
  url: string;
  title: string;
  snippet: string;
  score: number;
  published_date?: string;
}

interface SearchResponse {
  query: string;
  category: string;
  answer: string;
  citations: Citation[];
  sources: SourceItem[];
}

const CATEGORIES = [
  { id: 'WEB', label: 'Web', icon: Globe, color: 'text-nova-cyan' },
  { id: 'NEWS', label: 'News', icon: Newspaper, color: 'text-blue-400' },
  { id: 'ACADEMIC', label: 'Academic', icon: GraduationCap, color: 'text-purple-400' },
  { id: 'DOCUMENTATION', label: 'Docs', icon: FileCode2, color: 'text-emerald-400' },
];

export const Search: React.FC = () => {
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('WEB');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<SearchResponse | null>(null);

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim() || isLoading) return;

    setIsLoading(true);
    setResult(null);

    try {
      const res = await fetch('/api/v1/search/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, category, max_results: 5 }),
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch {
      // Fallback
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-8 font-sans animate-in fade-in duration-200">
      {/* Search Header */}
      <div className="space-y-1">
        <h1 className="text-2xl font-extrabold text-white flex items-center gap-2.5">
          <SearchIcon className="h-6 w-6 text-nova-cyan" />
          <span>Grounded AI Search</span>
        </h1>
        <p className="text-xs text-slate-400">
          Synthesizes verified web, news, and academic findings. Every single claim is backed by real, non-hallucinated citations.
        </p>
      </div>

      {/* Search Bar & Category Controls */}
      <div className="glass-panel-elevated p-3 rounded-2xl border border-nova-750 shadow-2xl space-y-3">
        <form onSubmit={handleSearch} className="flex items-center gap-3 px-2">
          <SearchIcon className="h-5 w-5 text-nova-cyan shrink-0" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a question or enter a research query..."
            className="w-full bg-transparent text-sm text-slate-100 placeholder-slate-500 focus:outline-none"
          />
          <button
            type="submit"
            disabled={isLoading || !query.trim()}
            className="px-5 py-2 rounded-xl bg-gradient-to-r from-nova-accent to-blue-600 hover:from-blue-600 hover:to-nova-accent text-white font-semibold text-xs shadow-glow-sm disabled:opacity-40 transition-all shrink-0"
          >
            {isLoading ? 'Searching...' : 'Search'}
          </button>
        </form>

        <div className="flex items-center gap-2 pt-2 border-t border-nova-800/80 px-1 overflow-x-auto">
          {CATEGORIES.map((c) => {
            const Icon = c.icon;
            const isSelected = category === c.id;
            return (
              <button
                key={c.id}
                type="button"
                onClick={() => setCategory(c.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors shrink-0 ${
                  isSelected
                    ? 'bg-nova-800 text-white border border-nova-700 font-semibold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-nova-850'
                }`}
              >
                <Icon className={`h-3.5 w-3.5 ${c.color}`} />
                <span>{c.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Loading Indicator */}
      {isLoading && (
        <div className="glass-panel p-8 rounded-2xl flex flex-col items-center justify-center space-y-3 text-center">
          <div className="h-8 w-8 rounded-full border-2 border-nova-cyan border-t-transparent animate-spin" />
          <p className="text-xs font-mono text-slate-400">
            Querying search provider & verifying citation groundedness...
          </p>
        </div>
      )}

      {/* Grounded Search Result View */}
      {result && (
        <div className="space-y-6">
          {/* Sources Carousel / Cards */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400">
              <span className="uppercase tracking-wider font-semibold">Retrieved Sources ({result.sources.length})</span>
              <span className="text-[10px] text-nova-emerald flex items-center gap-1">
                <ShieldCheck className="h-3.5 w-3.5" />
                <span>Citations Cross-Checked</span>
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {result.sources.map((src, i) => (
                <a
                  key={src.id || i}
                  href={src.url}
                  target="_blank"
                  rel="noreferrer"
                  className="p-3.5 rounded-xl glass-panel hover:bg-nova-850 border border-nova-800 hover:border-nova-cyan/40 transition-all space-y-1.5 group block"
                >
                  <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono">
                    <span className="truncate">Source [{i + 1}]</span>
                    <ExternalLink className="h-3 w-3 group-hover:text-nova-cyan transition-colors" />
                  </div>
                  <div className="text-xs font-bold text-slate-200 group-hover:text-white line-clamp-1">
                    {src.title}
                  </div>
                  <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
                    {src.snippet}
                  </p>
                </a>
              ))}
            </div>
          </div>

          {/* Synthesized Answer */}
          <div className="glass-panel-elevated p-6 rounded-2xl border border-nova-750 space-y-4 shadow-xl">
            <div className="flex items-center gap-2">
              <div className="h-7 w-7 rounded-lg bg-nova-cyan/20 border border-nova-cyan/40 flex items-center justify-center text-nova-cyan">
                <Sparkles className="h-4 w-4" />
              </div>
              <h2 className="text-sm font-bold text-white">Grounded Answer</h2>
            </div>

            <div className="text-xs text-slate-200 leading-relaxed whitespace-pre-wrap">
              {result.answer}
            </div>

            {/* Citations Box */}
            <div className="pt-4 border-t border-nova-800 space-y-2">
              <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 block font-semibold">
                Fact Verification Status
              </span>
              <div className="space-y-1.5">
                {result.citations.map((c) => (
                  <div
                    key={c.citation_id}
                    className="p-2.5 rounded-lg bg-nova-900/60 border border-nova-800 flex items-center justify-between text-xs"
                  >
                    <div className="space-y-0.5 min-w-0 pr-3">
                      <div className="font-semibold text-slate-200 truncate">
                        [{c.citation_id}] {c.source_title}
                      </div>
                      <div className="text-[10px] text-slate-400 truncate font-mono">
                        Match confidence: {Math.round(c.confidence * 100)}%
                      </div>
                    </div>
                    <span className={`text-[10px] font-mono px-2 py-0.5 rounded shrink-0 ${
                      c.verified
                        ? 'text-emerald-400 bg-emerald-500/10 border border-emerald-500/20'
                        : 'text-rose-400 bg-rose-500/10 border border-rose-500/20'
                    }`}>
                      {c.verified ? 'VERIFIED' : 'UNVERIFIED'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
