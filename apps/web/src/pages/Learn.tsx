import React, { useState, useEffect } from 'react';
import {
  BookOpen,
  GraduationCap,
  CheckCircle2,
  Award,
  Brain,
  Clock,
  Sparkles,
  HelpCircle,
  RotateCw,
  Send,
  Plus,
  ChevronRight,
  Flame,
  Check,
  X,
  Layers,
} from 'lucide-react';

interface Milestone {
  id: string;
  title: string;
  description: string;
  key_concepts: string[];
  completed: boolean;
}

interface StudyPlan {
  id: string;
  topic: string;
  goal: string;
  difficulty_level: string;
  timeframe_weeks: number;
  milestones: Milestone[];
  progress_percent: number;
}

interface QuizOption {
  id: number;
  text: string;
}

interface QuizQuestion {
  id: number;
  question: string;
  options: QuizOption[];
  correct_option_id: number;
  explanation: string;
}

interface QuizData {
  id: string;
  topic: string;
  difficulty: string;
  questions: QuizQuestion[];
}

interface QuizResult {
  quiz_id: string;
  total_questions: number;
  correct_count: number;
  score_percent: number;
  passed: boolean;
  results: {
    question_id: number;
    user_answer: number;
    correct_answer: number;
    is_correct: boolean;
    explanation: string;
  }[];
}

interface Flashcard {
  id: string;
  deck: string;
  front: string;
  back: string;
  mastery_level: number;
}

export const Learn: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'plans' | 'quiz' | 'socratic' | 'flashcards'>('plans');

  // Study plans state
  const [plans, setPlans] = useState<StudyPlan[]>([]);
  const [selectedPlan, setSelectedPlan] = useState<StudyPlan | null>(null);
  const [isCreatingPlan, setIsCreatingPlan] = useState<boolean>(false);
  const [newTopic, setNewTopic] = useState<string>('');
  const [newGoal, setNewGoal] = useState<string>('Staff Engineer Mastery');
  const [newDifficulty, setNewDifficulty] = useState<string>('Intermediate');

  // Quiz state
  const [quizTopic, setQuizTopic] = useState<string>('Distributed Systems & Consensus');
  const [activeQuiz, setActiveQuiz] = useState<QuizData | null>(null);
  const [quizAnswers, setQuizAnswers] = useState<Record<number, number>>({});
  const [quizResult, setQuizResult] = useState<QuizResult | null>(null);
  const [isLoadingQuiz, setIsLoadingQuiz] = useState<boolean>(false);

  // Socratic state
  const [socraticTopic, setSocraticTopic] = useState<string>('CAP Theorem Trade-offs');
  const [socraticInput, setSocraticInput] = useState<string>('');
  const [socraticChat, setSocraticChat] = useState<{ sender: 'user' | 'tutor'; text: string; hint?: string }[]>([
    {
      sender: 'tutor',
      text: "Greetings. I am your Socratic Tutor. Instead of spoon-feeding solutions, I will help you reason through complex computer science concepts from first principles. What concept would you like to dissect today?",
    },
  ]);
  const [isSocraticThinking, setIsSocraticThinking] = useState<boolean>(false);

  // Flashcards state
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [currentFcIndex, setCurrentFcIndex] = useState<number>(0);
  const [isFlipped, setIsFlipped] = useState<boolean>(false);

  useEffect(() => {
    fetchPlans();
    fetchFlashcards();
  }, []);

  const fetchPlans = async () => {
    try {
      const res = await fetch('/api/v1/learning/plans');
      if (res.ok) {
        const data = await res.json();
        setPlans(data);
        if (data.length > 0) setSelectedPlan(data[0]);
      }
    } catch (err) {
      console.error('Failed to load study plans', err);
    }
  };

  const fetchFlashcards = async () => {
    try {
      const res = await fetch('/api/v1/learning/flashcards');
      if (res.ok) {
        const data = await res.json();
        setFlashcards(data);
      }
    } catch (err) {
      console.error('Failed to load flashcards', err);
    }
  };

  const handleCreatePlan = async () => {
    if (!newTopic.trim()) return;
    try {
      const res = await fetch('/api/v1/learning/plans', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: newTopic,
          target_role_or_goal: newGoal,
          difficulty_level: newDifficulty,
          timeframe_weeks: 4,
        }),
      });
      if (res.ok) {
        const created = await res.json();
        setPlans([created, ...plans]);
        setSelectedPlan(created);
        setIsCreatingPlan(false);
        setNewTopic('');
      }
    } catch (err) {
      console.error('Failed to create study plan', err);
    }
  };

  const handleGenerateQuiz = async () => {
    if (!quizTopic.trim() || isLoadingQuiz) return;
    setIsLoadingQuiz(true);
    setQuizResult(null);
    setQuizAnswers({});
    try {
      const res = await fetch('/api/v1/learning/quiz/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: quizTopic, difficulty: 'Intermediate', num_questions: 3 }),
      });
      if (res.ok) {
        const data = await res.json();
        setActiveQuiz(data);
      }
    } catch (err) {
      console.error('Failed to generate quiz', err);
    } finally {
      setIsLoadingQuiz(false);
    }
  };

  const handleSubmitQuiz = async () => {
    if (!activeQuiz) return;
    try {
      const res = await fetch('/api/v1/learning/quiz/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quiz_id: activeQuiz.id, answers: quizAnswers }),
      });
      if (res.ok) {
        const data = await res.json();
        setQuizResult(data);
      }
    } catch (err) {
      console.error('Failed to submit quiz', err);
    }
  };

  const handleSocraticSend = async () => {
    if (!socraticInput.trim() || isSocraticThinking) return;
    const userMsg = socraticInput;
    setSocraticInput('');
    setSocraticChat((prev) => [...prev, { sender: 'user', text: userMsg }]);
    setIsSocraticThinking(true);
    try {
      const res = await fetch('/api/v1/learning/socratic/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: socraticTopic, student_statement: userMsg }),
      });
      if (res.ok) {
        const data = await res.json();
        setSocraticChat((prev) => [
          ...prev,
          {
            sender: 'tutor',
            text: `${data.coaching_question}\n\n💡 Focus Area: ${data.thought_prompt}`,
            hint: data.hint,
          },
        ]);
      }
    } catch (err) {
      console.error('Socratic error', err);
    } finally {
      setIsSocraticThinking(false);
    }
  };

  return (
    <div className="h-[calc(100vh-3.5rem)] flex flex-col bg-nova-950 font-sans overflow-hidden">
      {/* Top Navigation Tabs */}
      <div className="h-14 border-b border-nova-800 bg-nova-900/80 px-8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <BookOpen className="h-5 w-5 text-amber-400" />
          <span className="text-sm font-bold text-white">NOVA Learning OS</span>
        </div>

        <div className="flex items-center gap-2">
          {[
            { id: 'plans', label: 'Study Plans & Syllabus', icon: GraduationCap },
            { id: 'quiz', label: 'Diagnostic Quizzes', icon: HelpCircle },
            { id: 'socratic', label: 'Socratic AI Tutor', icon: Brain },
            { id: 'flashcards', label: 'Spaced Repetition', icon: Layers },
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                  activeTab === tab.id
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30 shadow-glow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-nova-850'
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto p-8 max-w-6xl mx-auto w-full">
        {/* TAB 1: STUDY PLANS */}
        {activeTab === 'plans' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <GraduationCap className="h-5 w-5 text-amber-400" />
                  <span>Adaptive Study Plans</span>
                </h2>
                <p className="text-xs text-slate-400 mt-1">
                  Structured curriculum pathways with weekly milestones and core concept breakdowns.
                </p>
              </div>
              <button
                onClick={() => setIsCreatingPlan(true)}
                className="flex items-center gap-2 px-4 py-2 bg-amber-500 hover:bg-amber-400 text-nova-950 font-bold text-xs rounded-xl shadow-glow-sm transition-all"
              >
                <Plus className="h-4 w-4" />
                <span>New Study Plan</span>
              </button>
            </div>

            {/* Plans List and Active Plan Milestones */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Left Column: Plan Selector */}
              <div className="space-y-3">
                <span className="text-[11px] font-mono font-bold text-slate-400 uppercase tracking-wider">
                  Active Tracks ({plans.length})
                </span>
                <div className="space-y-2">
                  {plans.map((p) => (
                    <div
                      key={p.id}
                      onClick={() => setSelectedPlan(p)}
                      className={`p-4 rounded-xl border cursor-pointer transition-all ${
                        selectedPlan?.id === p.id
                          ? 'bg-nova-850 border-amber-500/50 shadow-glow-sm'
                          : 'bg-nova-900/60 border-nova-800 hover:border-nova-700'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-nova-800 text-amber-300">
                          {p.difficulty_level}
                        </span>
                        <span className="text-[11px] text-slate-500 font-mono">{p.timeframe_weeks}w</span>
                      </div>
                      <h4 className="text-xs font-bold text-white mt-2 line-clamp-1">{p.topic}</h4>
                      <p className="text-[11px] text-slate-400 line-clamp-1 mt-0.5">{p.goal}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Right Column: Milestones */}
              <div className="md:col-span-2 space-y-4">
                {selectedPlan && (
                  <div className="p-6 rounded-2xl bg-nova-900 border border-nova-800 space-y-5">
                    <div>
                      <div className="flex items-center justify-between">
                        <h3 className="text-sm font-bold text-white">{selectedPlan.topic}</h3>
                        <span className="text-xs text-amber-400 font-semibold">{selectedPlan.goal}</span>
                      </div>
                      <div className="w-full bg-nova-950 rounded-full h-2 mt-3 overflow-hidden border border-nova-850">
                        <div className="bg-amber-400 h-full w-1/3 rounded-full" />
                      </div>
                    </div>

                    <div className="space-y-3">
                      <span className="text-xs font-bold text-slate-300 font-mono uppercase tracking-wider">
                        Curriculum Milestones
                      </span>
                      <div className="space-y-3">
                        {selectedPlan.milestones.map((m, idx) => (
                          <div
                            key={m.id}
                            className="p-4 rounded-xl bg-nova-950 border border-nova-850 space-y-2"
                          >
                            <div className="flex items-center justify-between">
                              <span className="text-xs font-bold text-white flex items-center gap-2">
                                <span className="h-5 w-5 rounded-full bg-amber-500/20 text-amber-300 text-[10px] flex items-center justify-center font-mono">
                                  {idx + 1}
                                </span>
                                {m.title}
                              </span>
                              <span className="text-[10px] font-mono text-slate-500">Milestone {idx + 1}</span>
                            </div>
                            <p className="text-xs text-slate-400">{m.description}</p>
                            <div className="flex flex-wrap gap-1.5 pt-1">
                              {m.key_concepts.map((c, i) => (
                                <span
                                  key={i}
                                  className="text-[10px] font-mono px-2 py-0.5 rounded bg-nova-900 text-slate-300 border border-nova-800"
                                >
                                  {c}
                                </span>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Modal: New Plan */}
            {isCreatingPlan && (
              <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                <div className="bg-nova-900 border border-nova-800 rounded-2xl p-6 w-full max-w-md space-y-4">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-amber-400" />
                    <span>Create Adaptive Study Plan</span>
                  </h3>
                  <div className="space-y-3 text-xs">
                    <div>
                      <label className="text-slate-400 block mb-1">Subject / Domain</label>
                      <input
                        type="text"
                        value={newTopic}
                        onChange={(e) => setNewTopic(e.target.value)}
                        placeholder="e.g. Distributed Database Engineering"
                        className="w-full bg-nova-950 border border-nova-800 rounded-lg p-2 text-white focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="text-slate-400 block mb-1">Target Mastery Goal</label>
                      <input
                        type="text"
                        value={newGoal}
                        onChange={(e) => setNewGoal(e.target.value)}
                        placeholder="e.g. Lead Architect Competency"
                        className="w-full bg-nova-950 border border-nova-800 rounded-lg p-2 text-white focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="text-slate-400 block mb-1">Target Difficulty</label>
                      <select
                        value={newDifficulty}
                        onChange={(e) => setNewDifficulty(e.target.value)}
                        className="w-full bg-nova-950 border border-nova-800 rounded-lg p-2 text-white focus:outline-none"
                      >
                        <option value="Beginner">Beginner (Foundations)</option>
                        <option value="Intermediate">Intermediate (Core Concepts)</option>
                        <option value="Advanced">Advanced (Systems & Scale)</option>
                      </select>
                    </div>
                  </div>
                  <div className="flex justify-end gap-2 pt-2">
                    <button
                      onClick={() => setIsCreatingPlan(false)}
                      className="px-3 py-1.5 rounded-lg bg-nova-800 text-slate-300 text-xs"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleCreatePlan}
                      className="px-4 py-1.5 rounded-lg bg-amber-500 text-nova-950 font-bold text-xs"
                    >
                      Generate Plan
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: DIAGNOSTIC QUIZ */}
        {activeTab === 'quiz' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <HelpCircle className="h-5 w-5 text-amber-400" />
                  <span>Interactive Diagnostic Quizzes</span>
                </h2>
                <p className="text-xs text-slate-400 mt-1">
                  Test your mastery with machine-graded conceptual problems and instantaneous rationale.
                </p>
              </div>
            </div>

            {/* Quiz Generator Input Bar */}
            <div className="p-4 rounded-xl bg-nova-900 border border-nova-800 flex items-center gap-3">
              <input
                type="text"
                value={quizTopic}
                onChange={(e) => setQuizTopic(e.target.value)}
                placeholder="Enter topic for diagnostic quiz..."
                className="flex-1 bg-nova-950 border border-nova-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none"
              />
              <button
                onClick={handleGenerateQuiz}
                disabled={isLoadingQuiz}
                className="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-nova-950 font-bold text-xs rounded-lg transition-all"
              >
                {isLoadingQuiz ? 'Generating...' : 'Start Quiz'}
              </button>
            </div>

            {/* Active Quiz Runner */}
            {activeQuiz && (
              <div className="p-6 rounded-2xl bg-nova-900 border border-nova-800 space-y-6">
                <div className="flex items-center justify-between border-b border-nova-800 pb-3">
                  <h3 className="text-sm font-bold text-white">{activeQuiz.topic} Diagnostic</h3>
                  <span className="text-xs font-mono text-amber-400">
                    {activeQuiz.questions.length} Questions
                  </span>
                </div>

                <div className="space-y-6">
                  {activeQuiz.questions.map((q, idx) => (
                    <div key={q.id} className="space-y-3">
                      <div className="text-xs font-bold text-white flex items-start gap-2">
                        <span className="text-amber-400 font-mono">Q{idx + 1}.</span>
                        <span>{q.question}</span>
                      </div>
                      <div className="space-y-2 pl-6">
                        {q.options.map((opt) => (
                          <label
                            key={opt.id}
                            className={`flex items-center gap-3 p-3 rounded-xl border text-xs cursor-pointer transition-all ${
                              quizAnswers[q.id] === opt.id
                                ? 'bg-amber-500/10 border-amber-500 text-amber-200'
                                : 'bg-nova-950 border-nova-850 text-slate-300 hover:bg-nova-850'
                            }`}
                          >
                            <input
                              type="radio"
                              name={`q-${q.id}`}
                              checked={quizAnswers[q.id] === opt.id}
                              onChange={() =>
                                setQuizAnswers({ ...quizAnswers, [q.id]: opt.id })
                              }
                              className="accent-amber-400"
                            />
                            <span>{opt.text}</span>
                          </label>
                        ))}
                      </div>

                      {/* If evaluated, show explanation */}
                      {quizResult && (
                        <div className="pl-6 pt-1">
                          {quizResult.results.find((r) => r.question_id === q.id)?.is_correct ? (
                            <div className="text-[11px] text-emerald-400 flex items-center gap-1.5 bg-emerald-500/10 p-2.5 rounded-lg border border-emerald-500/20">
                              <CheckCircle2 className="h-4 w-4 shrink-0" />
                              <span>Correct! {q.explanation}</span>
                            </div>
                          ) : (
                            <div className="text-[11px] text-rose-400 flex items-center gap-1.5 bg-rose-500/10 p-2.5 rounded-lg border border-rose-500/20">
                              <X className="h-4 w-4 shrink-0" />
                              <span>Incorrect. Correct concept: {q.explanation}</span>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                {!quizResult ? (
                  <div className="flex justify-end pt-4 border-t border-nova-800">
                    <button
                      onClick={handleSubmitQuiz}
                      className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-xl shadow-glow-sm transition-all"
                    >
                      Submit for Evaluation
                    </button>
                  </div>
                ) : (
                  <div className="p-4 rounded-xl bg-nova-950 border border-nova-800 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Award className="h-6 w-6 text-amber-400" />
                      <div>
                        <div className="text-sm font-bold text-white">
                          Score: {quizResult.score_percent}% ({quizResult.correct_count} /{' '}
                          {quizResult.total_questions})
                        </div>
                        <div className="text-xs text-slate-400">
                          {quizResult.passed ? '✓ Passing Standard Met' : 'Needs Further Review'}
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={handleGenerateQuiz}
                      className="px-4 py-1.5 bg-nova-800 hover:bg-nova-750 text-white text-xs rounded-lg"
                    >
                      Retry Another Set
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* TAB 3: SOCRATIC AI TUTOR */}
        {activeTab === 'socratic' && (
          <div className="space-y-4 h-[calc(100vh-12rem)] flex flex-col">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <Brain className="h-5 w-5 text-purple-400" />
                  <span>Socratic AI Coach</span>
                </h2>
                <p className="text-xs text-slate-400 mt-1">
                  Guided self-discovery: Test your reasoning, answer thought questions, and expose logical fallacies.
                </p>
              </div>
            </div>

            {/* Socratic Chat Box */}
            <div className="flex-1 bg-nova-900 border border-nova-800 rounded-2xl flex flex-col overflow-hidden">
              <div className="flex-1 p-5 overflow-y-auto space-y-4">
                {socraticChat.map((msg, i) => (
                  <div
                    key={i}
                    className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-2xl p-4 rounded-2xl text-xs leading-relaxed ${
                        msg.sender === 'user'
                          ? 'bg-amber-500 text-nova-950 font-medium'
                          : 'bg-nova-950 text-slate-200 border border-nova-850'
                      }`}
                    >
                      <div className="whitespace-pre-wrap">{msg.text}</div>
                      {msg.hint && (
                        <div className="mt-3 pt-2 border-t border-nova-800 text-[11px] text-amber-300 font-mono">
                          🔍 Hint: {msg.hint}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                {isSocraticThinking && (
                  <div className="text-xs text-amber-400 animate-pulse font-mono">
                    Socratic Coach formulating pedagogical thought question...
                  </div>
                )}
              </div>

              {/* Chat Input */}
              <div className="p-3 border-t border-nova-800 bg-nova-950 flex items-center gap-2">
                <input
                  type="text"
                  value={socraticInput}
                  onChange={(e) => setSocraticInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSocraticSend()}
                  placeholder="Explain your understanding or answer the tutor's question..."
                  className="flex-1 bg-transparent px-3 py-2 text-xs text-white focus:outline-none"
                />
                <button
                  onClick={handleSocraticSend}
                  disabled={!socraticInput.trim() || isSocraticThinking}
                  className="p-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-nova-950 transition-colors"
                >
                  <Send className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: FLASHCARDS */}
        {activeTab === 'flashcards' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Layers className="h-5 w-5 text-emerald-400" />
                <span>Spaced Repetition Flashcards</span>
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Active recall system with algorithmically adjusted intervals based on recall confidence.
              </p>
            </div>

            {flashcards.length > 0 ? (
              <div className="flex flex-col items-center space-y-6">
                {/* Flashcard Body */}
                <div
                  onClick={() => setIsFlipped(!isFlipped)}
                  className="w-full max-w-xl h-72 rounded-3xl bg-nova-900 border border-nova-800 hover:border-emerald-400/50 cursor-pointer p-8 flex flex-col justify-between shadow-2xl transition-all select-none"
                >
                  <div className="flex items-center justify-between text-xs text-slate-400">
                    <span className="font-mono text-emerald-400 uppercase tracking-wider">
                      {flashcards[currentFcIndex].deck}
                    </span>
                    <span className="font-mono">
                      Card {currentFcIndex + 1} of {flashcards.length}
                    </span>
                  </div>

                  <div className="text-center my-auto">
                    <div className="text-[11px] font-mono text-slate-500 mb-2 uppercase">
                      {isFlipped ? 'Answer / Concept' : 'Question (Click to reveal)'}
                    </div>
                    <div className="text-base font-semibold text-white leading-relaxed">
                      {isFlipped ? flashcards[currentFcIndex].back : flashcards[currentFcIndex].front}
                    </div>
                  </div>

                  <div className="flex items-center justify-center text-[10px] text-slate-500">
                    Click card to flip
                  </div>
                </div>

                {/* Rating Controls */}
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => {
                      setIsFlipped(false);
                      setCurrentFcIndex((prev) => (prev + 1) % flashcards.length);
                    }}
                    className="px-4 py-2 rounded-xl bg-rose-500/20 text-rose-300 text-xs font-semibold hover:bg-rose-500/30"
                  >
                    Hard (Review in 10m)
                  </button>
                  <button
                    onClick={() => {
                      setIsFlipped(false);
                      setCurrentFcIndex((prev) => (prev + 1) % flashcards.length);
                    }}
                    className="px-4 py-2 rounded-xl bg-amber-500/20 text-amber-300 text-xs font-semibold hover:bg-amber-500/30"
                  >
                    Good (Review in 1d)
                  </button>
                  <button
                    onClick={() => {
                      setIsFlipped(false);
                      setCurrentFcIndex((prev) => (prev + 1) % flashcards.length);
                    }}
                    className="px-4 py-2 rounded-xl bg-emerald-500/20 text-emerald-300 text-xs font-semibold hover:bg-emerald-500/30"
                  >
                    Easy (Review in 3d)
                  </button>
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-400">Loading flashcards...</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
