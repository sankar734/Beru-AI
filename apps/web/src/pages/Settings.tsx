import React, { useState, useEffect } from 'react';
import {
  Settings as SettingsIcon,
  Shield,
  Sliders,
  Network,
  Database,
  Github,
  Play,
  CheckCircle2,
  AlertTriangle,
  FolderGit2
} from 'lucide-react';
import { useAuthStore } from '../stores/useAuthStore';

interface MCPServer {
  server_id: string;
  name: string;
  transport: string;
  status: string;
  description: string;
  tools_count: number;
  resources_count: number;
}

export const Settings: React.FC = () => {
  const { user } = useAuthStore();
  const [mcpServers, setMcpServers] = useState<MCPServer[]>([]);
  const [testResult, setTestResult] = useState<any | null>(null);
  const [isCallingMcp, setIsCallingMcp] = useState<boolean>(false);

  useEffect(() => {
    fetchMcpServers();
  }, []);

  const fetchMcpServers = async () => {
    try {
      const res = await fetch('/api/v1/mcp/servers');
      if (res.ok) {
        const data = await res.json();
        setMcpServers(data);
      }
    } catch (err) {
      console.error('Failed to load MCP servers', err);
    }
  };

  const handleTestCall = async (serverId: string, toolName: string) => {
    setIsCallingMcp(true);
    setTestResult(null);
    try {
      const res = await fetch('/api/v1/mcp/call', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          server_id: serverId,
          tool_name: toolName,
          arguments: { org: 'nova-intelligence', sql: 'SELECT * FROM users' },
          human_approved: false
        })
      });
      const data = await res.json();
      setTestResult({ status_code: res.status, ...data });
    } catch (err) {
      console.error('MCP test call failed', err);
    } finally {
      setIsCallingMcp(false);
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-6">
      <div className="space-y-1">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <SettingsIcon className="h-5 w-5 text-slate-400" />
          <span>System Settings & Preferences</span>
        </h1>
        <p className="text-xs text-slate-400">
          Configure model providers, MCP connected apps, privacy boundaries, and notifications.
        </p>
      </div>

      <div className="space-y-4">
        {/* User Profile */}
        <div className="glass-panel p-6 rounded-2xl space-y-3 border border-nova-750">
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300">Operator Profile</h3>
          <div className="grid grid-cols-2 gap-4 text-xs">
            <div>
              <span className="text-slate-500 block">Name</span>
              <span className="text-white font-semibold">{user?.name || 'Nova Operator'}</span>
            </div>
            <div>
              <span className="text-slate-500 block">Email</span>
              <span className="text-white font-semibold">{user?.email || 'operator@novax.local'}</span>
            </div>
          </div>
        </div>

        {/* Phase 25: Model Context Protocol (MCP) & Connected Apps */}
        <div className="glass-panel p-6 rounded-2xl space-y-4 border border-nova-750">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <Network className="h-4 w-4 text-emerald-400" />
              <span>Connected Apps & MCP Protocol (Model Context Protocol)</span>
            </h3>
            <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
              ACTIVE STANDARD
            </span>
          </div>

          <p className="text-xs text-slate-400">
            Standardized JSON-RPC 2.0 adapters connecting external datasets, dev environments, and databases.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {mcpServers.map((server) => (
              <div key={server.server_id} className="p-4 rounded-xl bg-nova-900/80 border border-nova-800 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white flex items-center gap-1.5">
                    {server.server_id === 'github' && <Github className="h-3.5 w-3.5 text-slate-300" />}
                    {server.server_id === 'postgres' && <Database className="h-3.5 w-3.5 text-blue-400" />}
                    {server.server_id === 'filesystem' && <FolderGit2 className="h-3.5 w-3.5 text-amber-400" />}
                    <span>{server.name}</span>
                  </span>
                  <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded">
                    {server.status}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 leading-snug">{server.description}</p>
                <div className="text-[10px] font-mono text-slate-500 flex items-center justify-between pt-1">
                  <span>{server.tools_count} Tools</span>
                  <span>{server.resources_count} Resources</span>
                </div>
                <div className="pt-2">
                  <button
                    onClick={() => {
                      const tool =
                        server.server_id === 'github'
                          ? 'github_list_repos'
                          : server.server_id === 'postgres'
                          ? 'postgres_inspect_schema'
                          : 'fs_list_directory';
                      handleTestCall(server.server_id, tool);
                    }}
                    disabled={isCallingMcp}
                    className="w-full py-1 rounded-lg bg-nova-800 hover:bg-nova-750 text-slate-300 text-[11px] font-mono border border-nova-700 transition flex items-center justify-center gap-1"
                  >
                    <Play className="h-3 w-3 text-emerald-400" />
                    <span>Test Tool Call</span>
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Live Test Response Drawer */}
          {testResult && (
            <div className="p-3.5 rounded-xl bg-nova-950 border border-nova-850 font-mono text-xs space-y-1.5">
              <div className="flex items-center justify-between text-[11px] text-slate-400">
                <span className="flex items-center gap-1.5 text-white">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                  <span>MCP Response ({testResult.tool_name || 'test'})</span>
                </span>
                <span>{testResult.execution_time_ms ? `${testResult.execution_time_ms} ms` : 'Blocked by policy'}</span>
              </div>
              <pre className="text-slate-300 text-[11px] whitespace-pre-wrap max-h-40 overflow-y-auto pt-1">
                {JSON.stringify(testResult, null, 2)}
              </pre>
            </div>
          )}
        </div>

        {/* AI Model Preferences */}
        <div className="glass-panel p-6 rounded-2xl space-y-4 border border-nova-750">
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <Sliders className="h-4 w-4 text-nova-accent" />
            <span>AI Model & Provider Routing</span>
          </h3>

          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-3 rounded-xl bg-nova-900/60 border border-nova-800">
              <div>
                <div className="font-semibold text-white">Default Model Routing</div>
                <div className="text-[11px] text-slate-400">Auto-routes between quick, reasoning, and vision pipelines</div>
              </div>
              <span className="font-mono text-nova-accent bg-nova-accent/10 px-2.5 py-1 rounded">AUTO DYNAMIC</span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-nova-900/60 border border-nova-800">
              <div>
                <div className="font-semibold text-white">Local-Only AI Fallback</div>
                <div className="text-[11px] text-slate-400">Enforce zero-cloud transmission for sensitive desktop files</div>
              </div>
              <input type="checkbox" className="rounded border-nova-700 text-nova-accent" />
            </div>
          </div>
        </div>

        {/* Security & Memory Policy */}
        <div className="glass-panel p-6 rounded-2xl space-y-4 border border-nova-750">
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <Shield className="h-4 w-4 text-emerald-400" />
            <span>Memory & Privacy Policy</span>
          </h3>

          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-3 rounded-xl bg-nova-900/60 border border-nova-800">
              <div>
                <div className="font-semibold text-white">Long-Term Memory Retention</div>
                <div className="text-[11px] text-slate-400">Allows NOVA to remember preferences and recurring workflows</div>
              </div>
              <input type="checkbox" defaultChecked className="rounded border-nova-700 text-nova-accent" />
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-nova-900/60 border border-nova-800">
              <div>
                <div className="font-semibold text-white">Consequential Action Barriers</div>
                <div className="text-[11px] text-slate-400">Always require confirmation for Level 3 and 4 actions</div>
              </div>
              <span className="font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded">ENFORCED</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
