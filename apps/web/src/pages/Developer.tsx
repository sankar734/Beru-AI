import React, { useState, useEffect } from 'react';
import {
  Terminal,
  Play,
  Square,
  RefreshCw,
  GitBranch,
  AlertCircle,
  CheckCircle2,
  Bug,
  FileCode,
  ShieldCheck,
  ChevronRight,
  Code2
} from 'lucide-react';

interface SupervisedService {
  id: string;
  name: string;
  command: string;
  status: string;
  port?: number;
  pid?: number;
  restarts_count: number;
  description: string;
}

interface GitStatus {
  branch: string;
  is_clean: boolean;
  modified_files: string[];
  untracked_files: string[];
  recent_commits: string[];
  workspace_root: string;
}

interface DiagnosticReport {
  has_error: boolean;
  error_type?: string;
  target_file?: string;
  target_line?: number;
  raw_message?: string;
  root_cause_summary: string;
  remediation_steps: string[];
}

interface TestRunResult {
  target: string;
  exit_code: number;
  success: boolean;
  passed_count: number;
  failed_count: number;
  duration_ms: number;
  stdout: string;
  stderr: string;
}

export const Developer: React.FC = () => {
  const [services, setServices] = useState<SupervisedService[]>([]);
  const [gitStatus, setGitStatus] = useState<GitStatus | null>(null);
  const [selectedServiceLogs, setSelectedServiceLogs] = useState<{ id: string; logs: string[] } | null>(null);
  const [activeTab, setActiveTab] = useState<'services' | 'tests' | 'diagnostics' | 'diff'>('services');

  // Diagnostics state
  const [logInput, setLogInput] = useState<string>(
    'Traceback (most recent call last):\n  File "apps/api/routers/demo.py", line 42, in handle_request\n    result = calculate_metrics(data)\nValueError: invalid literal for int() with base 10: "abc"'
  );
  const [diagnosticReport, setDiagnosticReport] = useState<DiagnosticReport | null>(null);
  const [isDiagnosing, setIsDiagnosing] = useState(false);

  // Test Runner state
  const [testTarget, setTestTarget] = useState<string>('tests/test_phase0.py');
  const [testResult, setTestResult] = useState<TestRunResult | null>(null);
  const [isRunningTests, setIsRunningTests] = useState(false);

  // Diff state
  const [origCode, setOrigCode] = useState<string>('def calculate(a, b):\n    return a + b');
  const [newCode, setNewCode] = useState<string>('def calculate(a, b):\n    # Enhanced with safety guard\n    if a is None or b is None:\n        return 0\n    return a + b');
  const [diffResult, setDiffResult] = useState<{ diff: string; additions: number; deletions: number } | null>(null);

  const token = localStorage.getItem('nova_token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  };

  useEffect(() => {
    fetchServices();
    fetchGitStatus();
  }, []);

  const fetchServices = async () => {
    try {
      const res = await fetch('/api/v1/developer/services', { headers });
      if (res.ok) {
        const data = await res.json();
        setServices(data);
      }
    } catch (err) {
      console.error('Failed to fetch services', err);
    }
  };

  const fetchGitStatus = async () => {
    try {
      const res = await fetch('/api/v1/developer/git/status', { headers });
      if (res.ok) {
        const data = await res.json();
        setGitStatus(data);
      }
    } catch (err) {
      console.error('Failed to fetch git status', err);
    }
  };

  const handleRestartService = async (serviceId: string) => {
    try {
      const res = await fetch(`/api/v1/developer/services/${serviceId}/restart`, {
        method: 'POST',
        headers
      });
      if (res.ok) {
        await fetchServices();
        handleViewLogs(serviceId);
      }
    } catch (err) {
      console.error('Failed to restart service', err);
    }
  };

  const handleViewLogs = async (serviceId: string) => {
    try {
      const res = await fetch(`/api/v1/developer/services/${serviceId}/logs?limit=40`, { headers });
      if (res.ok) {
        const data = await res.json();
        setSelectedServiceLogs({ id: serviceId, logs: data.logs || [] });
      }
    } catch (err) {
      console.error('Failed to fetch logs', err);
    }
  };

  const handleDiagnose = async () => {
    setIsDiagnosing(true);
    try {
      const res = await fetch('/api/v1/developer/diagnose', {
        method: 'POST',
        headers,
        body: JSON.stringify({ log_text: logInput })
      });
      if (res.ok) {
        const report = await res.json();
        setDiagnosticReport(report);
      }
    } catch (err) {
      console.error('Diagnostics failed', err);
    } finally {
      setIsDiagnosing(false);
    }
  };

  const handleRunTests = async () => {
    setIsRunningTests(true);
    try {
      const res = await fetch('/api/v1/developer/run-tests', {
        method: 'POST',
        headers,
        body: JSON.stringify({ test_target: testTarget })
      });
      if (res.ok) {
        const result = await res.json();
        setTestResult(result);
      }
    } catch (err) {
      console.error('Test execution failed', err);
    } finally {
      setIsRunningTests(false);
    }
  };

  const handleCalculateDiff = async () => {
    try {
      const res = await fetch('/api/v1/developer/diff', {
        method: 'POST',
        headers,
        body: JSON.stringify({ original_text: origCode, new_text: newCode, filename: 'solution.py' })
      });
      if (res.ok) {
        const data = await res.json();
        setDiffResult(data);
      }
    } catch (err) {
      console.error('Diff calculation failed', err);
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Terminal className="h-5 w-5 text-emerald-400" />
            <span>Developer Mode & Service Supervisor</span>
          </h1>
          <p className="text-xs text-slate-400">
            Phase 23: Process supervision, live git tracking, AST-verified code diffs, and auto-diagnostics.
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-1 bg-nova-900 border border-nova-800 p-1 rounded-xl text-xs">
          <button
            onClick={() => setActiveTab('services')}
            className={`px-3 py-1.5 rounded-lg transition-colors ${
              activeTab === 'services' ? 'bg-nova-800 text-white font-medium shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            Services & Git
          </button>
          <button
            onClick={() => setActiveTab('tests')}
            className={`px-3 py-1.5 rounded-lg transition-colors ${
              activeTab === 'tests' ? 'bg-nova-800 text-white font-medium shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            Sandboxed Tests
          </button>
          <button
            onClick={() => setActiveTab('diagnostics')}
            className={`px-3 py-1.5 rounded-lg transition-colors ${
              activeTab === 'diagnostics' ? 'bg-nova-800 text-white font-medium shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            Traceback Diagnostics
          </button>
          <button
            onClick={() => setActiveTab('diff')}
            className={`px-3 py-1.5 rounded-lg transition-colors ${
              activeTab === 'diff' ? 'bg-nova-800 text-white font-medium shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            Diff Engine
          </button>
        </div>
      </div>

      {/* Tab 1: Services & Git */}
      {activeTab === 'services' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {services.map((svc) => (
              <div key={svc.id} className="glass-panel p-5 rounded-2xl space-y-3 border border-nova-750">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white">{svc.name}</span>
                  <span
                    className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                      svc.status === 'ONLINE'
                        ? 'text-emerald-400 bg-emerald-500/10'
                        : 'text-amber-400 bg-amber-500/10'
                    }`}
                  >
                    {svc.status}
                  </span>
                </div>
                <p className="text-xs text-slate-400">{svc.description}</p>
                <div className="text-[11px] font-mono text-slate-500 space-y-0.5">
                  <div>PID: {svc.pid || 'N/A'} {svc.port ? `• Port: ${svc.port}` : ''}</div>
                  <div>Restarts: {svc.restarts_count}</div>
                </div>
                <div className="flex items-center gap-2 pt-2">
                  <button
                    onClick={() => handleRestartService(svc.id)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-nova-800 hover:bg-nova-750 text-slate-200 text-xs border border-nova-700 transition"
                  >
                    <RefreshCw className="h-3 w-3" />
                    <span>Restart</span>
                  </button>
                  <button
                    onClick={() => handleViewLogs(svc.id)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-nova-850 hover:bg-nova-800 text-slate-400 text-xs transition"
                  >
                    <span>View Logs</span>
                  </button>
                </div>
              </div>
            ))}

            {/* Git Health Status Card */}
            {gitStatus && (
              <div className="glass-panel p-5 rounded-2xl space-y-3 border border-nova-750">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white">Git Health Status</span>
                  <span
                    className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                      gitStatus.is_clean ? 'text-blue-400 bg-blue-500/10' : 'text-amber-400 bg-amber-500/10'
                    }`}
                  >
                    {gitStatus.is_clean ? 'CLEAN' : 'DIRTY'}
                  </span>
                </div>
                <p className="text-xs text-slate-400">
                  Branch: <strong className="text-slate-200">{gitStatus.branch}</strong> • {gitStatus.modified_files.length} modified
                </p>
                <div className="text-[11px] font-mono text-slate-400 space-y-1">
                  <div className="flex items-center gap-1.5 text-slate-300">
                    <GitBranch className="h-3.5 w-3.5 text-blue-400" />
                    <span className="truncate">{gitStatus.recent_commits[0] || 'No commits'}</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Supervised Process Logs Drawer */}
          <div className="glass-panel p-4 rounded-2xl space-y-2 border border-nova-800 font-mono text-xs">
            <div className="flex items-center justify-between text-slate-400 pb-2 border-b border-nova-800">
              <span>Supervised Process Output {selectedServiceLogs ? `(${selectedServiceLogs.id})` : '(Live)'}</span>
              <span className="text-[10px] text-emerald-400">● LIVE BUFFER</span>
            </div>
            <div className="space-y-1 max-h-48 overflow-y-auto pt-1">
              {(selectedServiceLogs?.logs || [
                'INFO: Uvicorn running on http://127.0.0.1:8000',
                '[Vite] Ready in 218ms at http://localhost:5173/',
                '[Supervisor] All core daemons operating within nominal thresholds'
              ]).map((line, idx) => (
                <div key={idx} className="text-slate-300 leading-relaxed text-[11px]">
                  {line}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Sandboxed Tests */}
      {activeTab === 'tests' && (
        <div className="glass-panel p-6 rounded-2xl border border-nova-800 space-y-5">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-emerald-400" />
                <span>Isolated Pytest Execution Engine</span>
              </h2>
              <p className="text-xs text-slate-400">Run verified architectural test suites in an isolated sandbox.</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <input
              type="text"
              value={testTarget}
              onChange={(e) => setTestTarget(e.target.value)}
              placeholder="e.g. tests/test_phase0.py or tests/test_phase22.py"
              className="flex-1 bg-nova-900 border border-nova-750 px-4 py-2 rounded-xl text-xs text-white placeholder-slate-500 font-mono focus:outline-none focus:border-emerald-500"
            />
            <button
              onClick={handleRunTests}
              disabled={isRunningTests}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs transition disabled:opacity-50"
            >
              {isRunningTests ? <RefreshCw className="h-3.5 w-3.5 animate-spin" /> : <Play className="h-3.5 w-3.5" />}
              <span>{isRunningTests ? 'Running...' : 'Execute Suite'}</span>
            </button>
          </div>

          {testResult && (
            <div className="space-y-4 pt-2">
              <div className="flex items-center gap-4 text-xs font-mono">
                <span
                  className={`px-2.5 py-1 rounded-lg ${
                    testResult.success ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'
                  }`}
                >
                  {testResult.success ? '✓ PASSED' : '✕ FAILED'} (Exit: {testResult.exit_code})
                </span>
                <span className="text-slate-400">Passed: <strong className="text-white">{testResult.passed_count}</strong></span>
                <span className="text-slate-400">Failed: <strong className="text-white">{testResult.failed_count}</strong></span>
                <span className="text-slate-400">Duration: <strong className="text-white">{testResult.duration_ms} ms</strong></span>
              </div>

              <pre className="p-4 rounded-xl bg-nova-950 border border-nova-850 font-mono text-[11px] text-slate-300 max-h-60 overflow-y-auto whitespace-pre-wrap">
                {testResult.stdout || testResult.stderr || 'No stdout produced.'}
              </pre>
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Traceback Diagnostics */}
      {activeTab === 'diagnostics' && (
        <div className="glass-panel p-6 rounded-2xl border border-nova-800 space-y-5">
          <div>
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <Bug className="h-4 w-4 text-amber-400" />
              <span>Automated Traceback & Error Diagnosis</span>
            </h2>
            <p className="text-xs text-slate-400">Paste Python tracebacks or compiler logs for root-cause diagnosis.</p>
          </div>

          <textarea
            value={logInput}
            onChange={(e) => setLogInput(e.target.value)}
            rows={5}
            className="w-full bg-nova-900 border border-nova-750 p-3 rounded-xl text-xs text-white font-mono placeholder-slate-500 focus:outline-none focus:border-amber-500"
          />

          <button
            onClick={handleDiagnose}
            disabled={isDiagnosing}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-medium text-xs transition disabled:opacity-50"
          >
            {isDiagnosing ? <RefreshCw className="h-3.5 w-3.5 animate-spin" /> : <Bug className="h-3.5 w-3.5" />}
            <span>Analyze Traceback</span>
          </button>

          {diagnosticReport && (
            <div className="p-4 rounded-xl bg-nova-900/60 border border-nova-800 space-y-3">
              <div className="flex items-center gap-3">
                <span className="text-xs font-bold text-white">{diagnosticReport.root_cause_summary}</span>
                {diagnosticReport.error_type && (
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-400">
                    {diagnosticReport.error_type}
                  </span>
                )}
              </div>

              {diagnosticReport.target_file && (
                <div className="text-xs text-slate-400 font-mono">
                  Location: <span className="text-slate-200">{diagnosticReport.target_file}</span>
                  {diagnosticReport.target_line ? ` (Line ${diagnosticReport.target_line})` : ''}
                </div>
              )}

              {diagnosticReport.remediation_steps.length > 0 && (
                <div className="space-y-1 pt-1">
                  <div className="text-xs font-semibold text-slate-300">Recommended Remediation:</div>
                  <ul className="list-disc list-inside text-xs text-slate-400 space-y-0.5">
                    {diagnosticReport.remediation_steps.map((step, idx) => (
                      <li key={idx}>{step}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Tab 4: Diff Engine */}
      {activeTab === 'diff' && (
        <div className="glass-panel p-6 rounded-2xl border border-nova-800 space-y-5">
          <div>
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <Code2 className="h-4 w-4 text-emerald-400" />
              <span>Unified Diff & Patch Preview</span>
            </h2>
            <p className="text-xs text-slate-400">Compare proposed changes with AST-safe unified diff output.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-slate-400 block mb-1">Original Content</label>
              <textarea
                value={origCode}
                onChange={(e) => setOrigCode(e.target.value)}
                rows={6}
                className="w-full bg-nova-900 border border-nova-750 p-3 rounded-xl text-xs text-white font-mono focus:outline-none"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Modified Content</label>
              <textarea
                value={newCode}
                onChange={(e) => setNewCode(e.target.value)}
                rows={6}
                className="w-full bg-nova-900 border border-nova-750 p-3 rounded-xl text-xs text-white font-mono focus:outline-none"
              />
            </div>
          </div>

          <button
            onClick={handleCalculateDiff}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-nova-800 hover:bg-nova-750 text-white font-medium text-xs transition border border-nova-700"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            <span>Generate Unified Diff</span>
          </button>

          {diffResult && (
            <div className="space-y-3 pt-2">
              <div className="flex items-center gap-3 text-xs font-mono">
                <span className="text-emerald-400">+{diffResult.additions} additions</span>
                <span className="text-rose-400">-{diffResult.deletions} deletions</span>
              </div>
              <pre className="p-4 rounded-xl bg-nova-950 border border-nova-850 font-mono text-[11px] text-slate-300 max-h-60 overflow-y-auto whitespace-pre-wrap">
                {diffResult.diff || 'No differences detected.'}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
