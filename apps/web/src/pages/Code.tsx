import React from 'react';
import { Code2, Play, Terminal, ShieldAlert, Cpu } from 'lucide-react';

export const Code: React.FC = () => {
  return (
    <div className="flex h-[calc(100vh-3.5rem)] overflow-hidden">
      {/* Sidebar: File Tree */}
      <div className="w-56 border-r border-nova-800 bg-nova-900/50 p-4 space-y-3">
        <span className="text-xs font-bold text-slate-400 font-mono uppercase tracking-wider">Project Files</span>
        <div className="space-y-1 text-xs">
          <div className="px-2 py-1 rounded bg-nova-800 text-nova-cyan font-mono">main.py</div>
          <div className="px-2 py-1 rounded hover:bg-nova-850 text-slate-400 font-mono">utils.py</div>
          <div className="px-2 py-1 rounded hover:bg-nova-850 text-slate-400 font-mono">requirements.txt</div>
        </div>
      </div>

      {/* Center Editor Simulation */}
      <div className="flex-1 flex flex-col min-w-0 bg-nova-950">
        <div className="h-10 border-b border-nova-800 bg-nova-900/70 px-4 flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-mono text-slate-300">
            <span className="h-2 w-2 rounded-full bg-nova-cyan"></span>
            <span>main.py</span>
          </div>
          <button className="flex items-center gap-1.5 px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold shadow-glow-sm">
            <Play className="h-3 w-3" />
            <span>Run in Sandbox</span>
          </button>
        </div>

        <div className="flex-1 p-4 font-mono text-xs text-slate-200 overflow-y-auto bg-nova-950">
          <p className="text-slate-500"># NOVA X Code Sandbox - Isolated Subprocess Runner</p>
          <p className="text-slate-500"># Constraints: Max 5.0s CPU, 256MB RAM, No Host Secrets</p>
          <p className="mt-2"><span className="text-purple-400">def</span> <span className="text-blue-400">calculate_fibonacci</span>(n: int) -&gt; int:</p>
          <p className="pl-4">if n &lt;= 1:</p>
          <p className="pl-8">return n</p>
          <p className="pl-4">return calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)</p>
          <p className="mt-2"><span className="text-blue-400">print</span>(f"Fibonacci(10) = &#123;calculate_fibonacci(10)&#125;")</p>
        </div>

        {/* Output Console */}
        <div className="h-36 border-t border-nova-800 bg-nova-900/90 p-3 space-y-1 font-mono text-xs">
          <div className="flex items-center gap-2 text-slate-400 text-[11px]">
            <Terminal className="h-3.5 w-3.5 text-nova-emerald" />
            <span>Sandbox Terminal Output</span>
            <span className="text-[10px] text-slate-500">(Execution duration: 0.04s • RAM: 14MB)</span>
          </div>
          <div className="text-emerald-400">&gt; Fibonacci(10) = 55</div>
          <div className="text-slate-500">[Process finished with exit code 0]</div>
        </div>
      </div>
    </div>
  );
};
