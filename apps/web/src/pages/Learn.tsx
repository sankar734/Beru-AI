import React from 'react';
import { BookOpen, GraduationCap, CheckCircle2, Award, Brain, Clock } from 'lucide-react';

export const Learn: React.FC = () => {
  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      <div className="space-y-1">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <BookOpen className="h-5 w-5 text-amber-400" />
          <span>Learning OS & AI Tutor</span>
        </h1>
        <p className="text-xs text-slate-400">Personalized study plans, Socratic teaching, automated quizzes, and mastery tracking.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel p-5 rounded-2xl space-y-3 border border-nova-750">
          <GraduationCap className="h-5 w-5 text-amber-400" />
          <div className="text-sm font-bold text-white">Full Stack Python Track</div>
          <div className="text-xs text-slate-400">FastAPI, AsyncIO, Pytest, and Architecture Patterns</div>
          <div className="w-full bg-nova-900 rounded-full h-2 overflow-hidden border border-nova-800">
            <div className="bg-amber-400 h-full w-3/4 rounded-full" />
          </div>
          <span className="text-[10px] text-amber-400 font-mono">75% Complete • 12 Lessons Mastered</span>
        </div>

        <div className="glass-panel p-5 rounded-2xl space-y-3 border border-nova-750">
          <Brain className="h-5 w-5 text-purple-400" />
          <div className="text-sm font-bold text-white">Aptitude & Reasoning</div>
          <div className="text-xs text-slate-400">Quantitative, Logical, and Data Interpretation</div>
          <div className="w-full bg-nova-900 rounded-full h-2 overflow-hidden border border-nova-800">
            <div className="bg-purple-400 h-full w-1/2 rounded-full" />
          </div>
          <span className="text-[10px] text-purple-400 font-mono">50% Complete • 40 Practice Problems</span>
        </div>

        <div className="glass-panel p-5 rounded-2xl space-y-3 border border-nova-750">
          <Award className="h-5 w-5 text-emerald-400" />
          <div className="text-sm font-bold text-white">Mock Interview Coach</div>
          <div className="text-xs text-slate-400">System Design and Senior Engineer Behavioral Rounds</div>
          <div className="w-full bg-nova-900 rounded-full h-2 overflow-hidden border border-nova-800">
            <div className="bg-emerald-400 h-full w-2/3 rounded-full" />
          </div>
          <span className="text-[10px] text-emerald-400 font-mono">Ready for Session 3</span>
        </div>
      </div>
    </div>
  );
};
