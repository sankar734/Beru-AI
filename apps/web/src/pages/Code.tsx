import React, { useState, useEffect } from 'react';
import {
  Code2,
  Play,
  Terminal,
  ShieldAlert,
  Cpu,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  Sparkles,
  Layers,
  Copy,
  Check,
  Clock,
} from 'lucide-react';

interface TemplateItem {
  id: string;
  name: string;
  description: string;
  code: string;
}

interface ExecutionResult {
  status: string;
  stdout: string;
  stderr: string;
  exit_code: number;
  duration_ms: number;
  language: string;
  security_warnings: string[];
}

export const Code: React.FC = () => {
  const [language, setLanguage] = useState<string>('python');
  const [code, setCode] = useState<string>(
    'import statistics\n\ndata = [15, 23, 89, 42, 67, 33, 91, 58]\nprint("NOVA X High-Performance Data Processing Sandbox")\nprint(f"Data: {data}")\nprint(f"Mean: {statistics.mean(data):.2f}")\nprint(f"StDev: {statistics.stdev(data):.2f}")'
  );
  const [stdin, setStdin] = useState<string>('');
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [result, setResult] = useState<ExecutionResult | null>(null);
  const [templates, setTemplates] = useState<Record<string, TemplateItem[]>>({});
  const [activeTab, setActiveTab] = useState<'output' | 'stdin' | 'security'>('output');
  const [copied, setCopied] = useState<boolean>(false);

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const res = await fetch('/api/v1/code/templates');
      if (res.ok) {
        const data = await res.json();
        if (data.templates) {
          setTemplates(data.templates);
        }
      }
    } catch (err) {
      console.error('Failed to load code templates', err);
    }
  };

  const handleRun = async () => {
    if (!code.trim() || isRunning) return;
    setIsRunning(true);
    setActiveTab('output');
    try {
      const res = await fetch('/api/v1/code/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          language,
          code,
          stdin,
          timeout_seconds: 5.0,
        }),
      });
      const data = await res.json();
      if (res.ok) {
        setResult(data);
      } else {
        setResult({
          status: 'ERROR',
          stdout: '',
          stderr: data.detail || 'Execution failed',
          exit_code: 1,
          duration_ms: 0,
          language,
          security_warnings: ['Sandbox error'],
        });
      }
    } catch (err: any) {
      setResult({
        status: 'ERROR',
        stdout: '',
        stderr: err.message || 'Sandbox execution request failed',
        exit_code: 1,
        duration_ms: 0,
        language,
        security_warnings: ['Request error occurred'],
      });
    } finally {
      setIsRunning(false);
    }
  };

  const loadTemplate = (tmpl: TemplateItem) => {
    setCode(tmpl.code);
  };

  const copyCode = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const currentLangTemplates = templates[language] || [];

  return (
    <div className="flex h-[calc(100vh-3.5rem)] overflow-hidden bg-nova-950 font-sans">
      {/* Left Sidebar: Templates & Language */}
      <div className="w-64 border-r border-nova-800 bg-nova-900/60 flex flex-col justify-between p-4">
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-slate-200 font-bold text-sm">
            <Code2 className="h-4 w-4 text-nova-cyan" />
            <span>Code Sandbox</span>
          </div>

          {/* Language Selector */}
          <div className="space-y-1.5">
            <label className="text-[11px] font-semibold text-slate-400 font-mono uppercase tracking-wider">
              Runtime Environment
            </label>
            <div className="grid grid-cols-2 gap-1.5">
              {[
                { id: 'python', label: 'Python 3' },
                { id: 'javascript', label: 'Node.js' },
                { id: 'powershell', label: 'PowerShell' },
                { id: 'bash', label: 'Bash' },
              ].map((l) => (
                <button
                  key={l.id}
                  onClick={() => setLanguage(l.id)}
                  className={`px-2.5 py-1.5 rounded-lg text-xs font-mono font-medium text-left transition-colors ${
                    language === l.id
                      ? 'bg-nova-accent/20 border border-nova-accent/40 text-nova-cyan'
                      : 'bg-nova-850 hover:bg-nova-800 text-slate-400 border border-transparent'
                  }`}
                >
                  {l.label}
                </button>
              ))}
            </div>
          </div>

          {/* Preset Templates */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-semibold text-slate-400 font-mono uppercase tracking-wider">
                Snippets & Presets
              </span>
              <Sparkles className="h-3 w-3 text-amber-400" />
            </div>
            <div className="space-y-1.5">
              {currentLangTemplates.length === 0 ? (
                <p className="text-xs text-slate-500 italic">No templates for {language}</p>
              ) : (
                currentLangTemplates.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => loadTemplate(t)}
                    className="w-full text-left p-2 rounded-lg bg-nova-850/70 hover:bg-nova-800 border border-nova-800/80 hover:border-nova-700 transition-all group"
                  >
                    <div className="text-xs font-semibold text-slate-200 group-hover:text-nova-cyan transition-colors">
                      {t.name}
                    </div>
                    <div className="text-[10px] text-slate-400 line-clamp-1 mt-0.5">
                      {t.description}
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Security Isolation Card */}
        <div className="p-3 rounded-xl bg-nova-900 border border-nova-800 text-[11px] space-y-1.5">
          <div className="flex items-center gap-1.5 text-nova-cyan font-semibold">
            <ShieldAlert className="h-3.5 w-3.5" />
            <span>Zero-Trust Sandbox</span>
          </div>
          <p className="text-slate-400 leading-relaxed text-[10px]">
            Ephemeral directory, 5.0s hard execution limit, non-privilege sandbox, API secret redaction.
          </p>
        </div>
      </div>

      {/* Main Code Editor & Console */}
      <div className="flex-1 flex flex-col min-w-0 bg-nova-950">
        {/* Editor Toolbar */}
        <div className="h-11 border-b border-nova-800 bg-nova-900/80 px-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-xs font-mono text-slate-300">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>sandbox_script.{language === 'python' ? 'py' : language === 'javascript' ? 'js' : language === 'powershell' ? 'ps1' : 'sh'}</span>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-nova-800 text-slate-400">
              Isolated Subprocess
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={copyCode}
              title="Copy code"
              className="p-1.5 rounded-lg bg-nova-850 hover:bg-nova-800 text-slate-400 hover:text-slate-200 transition-colors"
            >
              {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
            </button>
            <button
              onClick={handleRun}
              disabled={isRunning || !code.trim()}
              className="flex items-center gap-1.5 px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white rounded-lg text-xs font-semibold shadow-glow-sm transition-all"
            >
              <Play className={`h-3 w-3 ${isRunning ? 'animate-spin' : ''}`} />
              <span>{isRunning ? 'Executing...' : 'Run in Sandbox'}</span>
            </button>
          </div>
        </div>

        {/* Code Editor Area */}
        <div className="flex-1 relative flex">
          {/* Line Numbers Simulation */}
          <div className="w-12 bg-nova-900/40 border-r border-nova-850 select-none py-3 px-2 text-right font-mono text-xs text-slate-600 space-y-1">
            {code.split('\n').map((_, i) => (
              <div key={i}>{i + 1}</div>
            ))}
          </div>

          {/* Text Area */}
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            spellCheck={false}
            className="flex-1 bg-transparent p-3 font-mono text-xs text-slate-100 placeholder-slate-600 focus:outline-none resize-none leading-relaxed"
            placeholder="Type or paste your code here..."
          />
        </div>

        {/* Console / Output Panel */}
        <div className="h-64 border-t border-nova-800 bg-nova-900/95 flex flex-col">
          {/* Console Header Tabs */}
          <div className="h-9 border-b border-nova-850 px-4 flex items-center justify-between bg-nova-900">
            <div className="flex items-center gap-4 text-xs font-mono">
              <button
                onClick={() => setActiveTab('output')}
                className={`flex items-center gap-1.5 py-1 border-b-2 font-medium transition-colors ${
                  activeTab === 'output'
                    ? 'border-nova-cyan text-nova-cyan'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                <Terminal className="h-3.5 w-3.5" />
                <span>Console Output</span>
                {result && (
                  <span
                    className={`ml-1 text-[10px] px-1.5 py-0.2 rounded font-semibold ${
                      result.status === 'SUCCESS'
                        ? 'bg-emerald-500/20 text-emerald-400'
                        : 'bg-rose-500/20 text-rose-400'
                    }`}
                  >
                    exit {result.exit_code}
                  </span>
                )}
              </button>
              <button
                onClick={() => setActiveTab('stdin')}
                className={`py-1 border-b-2 font-medium transition-colors ${
                  activeTab === 'stdin'
                    ? 'border-nova-cyan text-nova-cyan'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                Standard Input (STDIN)
              </button>
              {result && result.security_warnings.length > 0 && (
                <button
                  onClick={() => setActiveTab('security')}
                  className={`flex items-center gap-1 py-1 border-b-2 font-medium text-amber-400 ${
                    activeTab === 'security' ? 'border-amber-400' : 'border-transparent'
                  }`}
                >
                  <AlertTriangle className="h-3.5 w-3.5" />
                  <span>Security Alerts ({result.security_warnings.length})</span>
                </button>
              )}
            </div>

            {result && (
              <div className="flex items-center gap-3 text-[11px] font-mono text-slate-400">
                <span className="flex items-center gap-1">
                  <Clock className="h-3 w-3 text-slate-500" />
                  {result.duration_ms}ms
                </span>
                <span className="text-slate-600">•</span>
                <span className="text-slate-400 uppercase">{result.status}</span>
              </div>
            )}
          </div>

          {/* Console Content */}
          <div className="flex-1 p-3 overflow-y-auto font-mono text-xs">
            {activeTab === 'output' && (
              <div className="space-y-1">
                {!result && !isRunning && (
                  <div className="text-slate-500 italic">
                    Press "Run in Sandbox" above to execute the script in an isolated runtime.
                  </div>
                )}
                {isRunning && (
                  <div className="text-nova-cyan flex items-center gap-2">
                    <span className="animate-spin">⏳</span> Executing in ephemeral container...
                  </div>
                )}
                {result && result.stdout && (
                  <div className="text-slate-200 whitespace-pre-wrap">{result.stdout}</div>
                )}
                {result && result.stderr && (
                  <div className="text-rose-400 whitespace-pre-wrap">{result.stderr}</div>
                )}
                {result && !result.stdout && !result.stderr && (
                  <div className="text-slate-500 italic">[Process completed with no output]</div>
                )}
              </div>
            )}

            {activeTab === 'stdin' && (
              <div className="h-full flex flex-col">
                <span className="text-[11px] text-slate-500 mb-1">
                  Provide standard input lines to be passed to the process during execution:
                </span>
                <textarea
                  value={stdin}
                  onChange={(e) => setStdin(e.target.value)}
                  placeholder="Enter input to feed into process STDIN..."
                  className="flex-1 bg-nova-950 p-2 rounded border border-nova-800 text-slate-200 focus:outline-none resize-none font-mono text-xs"
                />
              </div>
            )}

            {activeTab === 'security' && result && (
              <div className="space-y-2">
                <div className="text-xs text-amber-400 font-semibold flex items-center gap-1.5">
                  <AlertTriangle className="h-4 w-4" />
                  <span>Security & Isolation Verifications</span>
                </div>
                <div className="space-y-1">
                  {result.security_warnings.map((w, idx) => (
                    <div key={idx} className="p-2 rounded bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs">
                      {w}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
