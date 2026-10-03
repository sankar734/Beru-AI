"""NOVA X - Learning OS Models
Data schemas for adaptive study plans, quizzes, Socratic coaching, and spaced repetition flashcards.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class StudyMilestone(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str
    description: str
    key_concepts: List[str] = Field(default_factory=list)
    completed: bool = False


class StudyPlanCreate(BaseModel):
    topic: str = Field(..., min_length=2, max_length=150)
    target_role_or_goal: Optional[str] = "Mastery"
    difficulty_level: str = Field(default="Intermediate", description="Beginner, Intermediate, Advanced")
    timeframe_weeks: int = Field(default=4, ge=1, le=52)


class StudyPlanResponse(BaseModel):
    id: str
    user_id: str
    topic: str
    goal: str
    difficulty_level: str
    timeframe_weeks: int
    milestones: List[StudyMilestone]
    progress_percent: float = 0.0
    created_at: str
    updated_at: str


class QuizOption(BaseModel):
    id: int
    text: str


class QuizQuestion(BaseModel):
    id: int
    question: str
    options: List[QuizOption]
    correct_option_id: int
    explanation: str


class QuizGenerateRequest(BaseModel):
    topic: str
    difficulty: str = "Intermediate"
    num_questions: int = Field(default=3, ge=1, le=10)


class QuizResponse(BaseModel):
    id: str
    topic: str
    difficulty: str
    questions: List[QuizQuestion]
    created_at: str


class QuizSubmissionRequest(BaseModel):
    quiz_id: str
    answers: Dict[int, int]  # question_id -> selected_option_id


class QuizQuestionResult(BaseModel):
    question_id: int
    user_answer: Optional[int]
    correct_answer: int
    is_correct: bool
    explanation: str


class QuizSubmissionResult(BaseModel):
    quiz_id: str
    total_questions: int
    correct_count: int
    score_percent: float
    passed: bool
    results: List[QuizQuestionResult]


class FlashcardItem(BaseModel):
    id: str = Field(default_factory=lambda: f"fc-{uuid.uuid4().hex[:8]}")
    deck: str
    front: str
    back: str
    mastery_level: int = Field(default=0, ge=0, le=5)
    last_reviewed: Optional[str] = None
    next_review: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SocraticPromptRequest(BaseModel):
    topic: str
    student_statement: str
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)


class SocraticResponse(BaseModel):
    coaching_question: str
    thought_prompt: str
    hint: Optional[str] = None
