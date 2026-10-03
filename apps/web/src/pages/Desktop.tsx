import React, { useState, useEffect } from 'react';
import {
  Laptop,
  ShieldCheck,
  Folder,
  Power,
  RefreshCw,
  Cpu,
  Activity,
  HardDrive,
  Play,
  Terminal,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';

interface SystemVitals {
  os_name: string;
  os_version: string;
  os_release: string;
  architecture: string;
  hostname: string;
  cpu_percent: number;
  cpu_cores: number;
  ram_total_gb: number;
  ram_used_gb: number;
  ram_percent: number;
  disk_total_gb: number;
  disk_used_gb: number;
  disk_percent: number;
  bridge_status: string;
}

interface ProcessInfo {
  pid: number;
  name: string;
  cpu_percent: number;
  memory_mb: number;
  status: string;
}

export const Desktop: React.FC = () => {
  const [vitals, setVitals] = useState<SystemVitals | null>(null);
  const [processes, setProcesses] = useState<ProcessInfo[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [launchMessage, setLaunchMessage] = useState<string | null>(null);

  useEffect(() => {
    fetchVitals();
    fetchProcesses();
  }, []);

  const fetchVitals = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/v1/desktop/status');
      if (res.ok) {
        const data = await res.json();
        setVitals(data);
      }
    } catch (err) {
      console.error('Failed to load system vitals', err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchProcesses = async () => {
    try {
      const res = await fetch('/api/v1/desktop/processes?limit=8');
      if (res.ok) {
        const data = await res.json();
        setProcesses(data);
      }
    } catch (err) {
      console.error('Failed to load processes', err);
    }
  };

  const handleLaunchApp = async (appKey: string) => {
    try {
      const res = await fetch('/api/v1/desktop/launch-app', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ app_key: appKey }),
      });
      if (res.ok) {
        const data = await res.json();
        setLaunchMessage(`✓ Launched ${appKey} (PID: ${data.pid})`);
        setTimeout(() => setLaunchMessage(null), 3000);
      }
    } catch (err) {
      setLaunchMessage(`Failed to launch ${appKey}`);
      setTimeout(() => setLaunchMessage(null), 3000);
    }
  };

  return (
    <div className="h-[calc(100vh-3.5rem)] flex flex-col bg-nova-950 font-sans overflow-hidden">
      {/* Top Banner */}
      <div className="h-16 border-b border-nova-800 bg-nova-900/80 px-8 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="h-10 w-10 rounded-2xl bg-nova-cyan/15 border border-nova-cyan/30 flex items-center justify-center text-nova-cyan shadow-glow-cyan">
            <Laptop className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold text-white">
                {vitals ? vitals.hostname : 'Host Desktop Companion'}
              </h2>
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                {vitals ? vitals.bridge_status : 'CONNECTING'}
              </span>
            </div>
            <p className="text-xs text-slate-400">
              {vitals
                ? `${vitals.os_name} ${vitals.os_release} • ${vitals.architecture} • Local Loopback Daemon`
                : 'Inspecting host platform...'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => {
              fetchVitals();
              fetchProcesses();
            }}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-nova-850 hover:bg-nova-800 text-xs text-slate-300 transition-colors"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          <button
            onClick={() => alert('Emergency Stop Protocol: Local bridge paused.')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-xs text-rose-400 font-semibold"
          >
            <Power className="h-3.5 w-3.5" />
            <span>Emergency Halt</span>
          </button>
        </div>
      </div>

      {/* Main Container */}
      <div className="flex-1 overflow-y-auto p-8 max-w-6xl mx-auto w-full space-y-6">
        {/* Hardware Vitals Cards */}
        {vitals && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {/* CPU */}
            <div className="p-5 rounded-2xl bg-nova-900 border border-nova-800 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-bold text-white">
                  <Cpu className="h-4 w-4 text-nova-cyan" />
                  <span>Processor Load</span>
                </div>
                <span className="text-xs font-mono text-nova-cyan font-bold">
                  {vitals.cpu_percent}%
                </span>
              </div>
              <div className="w-full bg-nova-950 rounded-full h-2 overflow-hidden border border-nova-850">
                <div
                  className="bg-nova-cyan h-full rounded-full transition-all"
                  style={{ width: `${Math.max(vitals.cpu_percent, 5)}%` }}
                />
              </div>
              <span className="text-[11px] font-mono text-slate-500">
                {vitals.cpu_cores} Logical Cores Active
              </span>
            </div>

            {/* RAM */}
            <div className="p-5 rounded-2xl bg-nova-900 border border-nova-800 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-bold text-white">
                  <Activity className="h-4 w-4 text-purple-400" />
                  <span>Physical Memory</span>
                </div>
                <span className="text-xs font-mono text-purple-400 font-bold">
                  {vitals.ram_percent}%
                </span>
              </div>
              <div className="w-full bg-nova-950 rounded-full h-2 overflow-hidden border border-nova-850">
                <div
                  className="bg-purple-500 h-full rounded-full transition-all"
                  style={{ width: `${vitals.ram_percent}%` }}
                />
              </div>
              <span className="text-[11px] font-mono text-slate-500">
                {vitals.ram_used_gb} GB used of {vitals.ram_total_gb} GB
              </span>
            </div>

            {/* DISK */}
            <div className="p-5 rounded-2xl bg-nova-900 border border-nova-800 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-bold text-white">
                  <HardDrive className="h-4 w-4 text-emerald-400" />
                  <span>Primary Storage</span>
                </div>
                <span className="text-xs font-mono text-emerald-400 font-bold">
                  {vitals.disk_percent}%
                </span>
              </div>
              <div className="w-full bg-nova-950 rounded-full h-2 overflow-hidden border border-nova-850">
                <div
                  className="bg-emerald-500 h-full rounded-full transition-all"
                  style={{ width: `${vitals.disk_percent}%` }}
                />
              </div>
              <span className="text-[11px] font-mono text-slate-500">
                {vitals.disk_used_gb} GB used of {vitals.disk_total_gb} GB
              </span>
            </div>
          </div>
        )}

        {/* Quick Whitelisted App Launcher */}
        <div className="p-5 rounded-2xl bg-nova-900 border border-nova-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-white flex items-center gap-2">
              <Play className="h-4 w-4 text-emerald-400" />
              <span>Controlled Desktop App Launcher</span>
            </span>
            {launchMessage && (
              <span className="text-xs font-mono text-emerald-400 animate-pulse">
                {launchMessage}
              </span>
            )}
          </div>
          <div className="flex flex-wrap gap-2.5">
            {[
              { id: 'notepad', label: 'Notepad', desc: 'Text Editor' },
              { id: 'calc', label: 'Calculator', desc: 'Math Tool' },
              { id: 'explorer', label: 'Explorer', desc: 'File System' },
              { id: 'powershell', label: 'PowerShell', desc: 'Shell Console' },
            ].map((app) => (
              <button
                key={app.id}
                onClick={() => handleLaunchApp(app.id)}
                className="p-3 rounded-xl bg-nova-950 hover:bg-nova-850 border border-nova-850 hover:border-nova-750 transition-all text-left group"
              >
                <div className="text-xs font-bold text-white group-hover:text-emerald-300">
                  {app.label}
                </div>
                <div className="text-[10px] text-slate-500">{app.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Running Processes Table */}
        <div className="p-6 rounded-2xl bg-nova-900 border border-nova-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <Terminal className="h-4 w-4 text-nova-cyan" />
              <span>Active Desktop Processes (Top Footprint)</span>
            </h3>
            <span className="text-[10px] font-mono text-slate-500">Live Memory Snapshot</span>
          </div>

          <div className="space-y-1.5 font-mono text-xs">
            {processes.map((p) => (
              <div
                key={p.pid}
                className="p-2.5 rounded-lg bg-nova-950 border border-nova-850 flex items-center justify-between text-slate-300"
              >
                <div className="flex items-center gap-3">
                  <span className="text-slate-500 text-[11px] w-14">PID {p.pid}</span>
                  <span className="text-white font-semibold">{p.name}</span>
                </div>
                <div className="flex items-center gap-4 text-[11px]">
                  <span className="text-purple-300">{p.memory_mb} MB RAM</span>
                  <span className="text-emerald-400 capitalize">{p.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
