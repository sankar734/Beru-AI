import React from 'react';
import { FileText, Upload, Database, Layers, CheckCircle } from 'lucide-react';

export const Files: React.FC = () => {
  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <FileText className="h-5 w-5 text-nova-cyan" />
            <span>Files & Hybrid RAG Intelligence</span>
          </h1>
          <p className="text-xs text-slate-400">PDFs, DOCX, CSVs, and code repositories parsed, chunked, and embedded into vector storage.</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-nova-accent hover:bg-blue-600 text-white font-semibold text-xs shadow-glow-sm">
          <Upload className="h-4 w-4" />
          <span>Upload File</span>
        </button>
      </div>

      <div className="glass-panel p-6 rounded-2xl border-2 border-dashed border-nova-800 hover:border-nova-accent/50 text-center space-y-2 cursor-pointer transition-colors">
        <Upload className="h-8 w-8 text-nova-accent mx-auto" />
        <div className="text-xs font-semibold text-slate-200">Drag & drop files here, or click to browse</div>
        <p className="text-[11px] text-slate-500">Supports PDF, DOCX, PPTX, XLSX, CSV, TXT, Markdown, JSON (up to 50MB)</p>
      </div>
    </div>
  );
};
