"""NOVA X - Learning OS Router
Provides endpoints for adaptive study plans, interactive quizzes, Socratic coaching, and flashcards.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import uuid

from apps.api.database import db_manager
from apps.api.auth import get_optional_user
from apps.api.models.learning import (
    StudyPlanCreate,
    StudyPlanResponse,
    StudyMilestone,
    QuizGenerateRequest,
    QuizResponse,
    QuizQuestion,
    QuizOption,
    QuizSubmissionRequest,
    QuizSubmissionResult,
    QuizQuestionResult,
    FlashcardItem,
    SocraticPromptRequest,
    SocraticResponse,
)

router = APIRouter(prefix="/learning", tags=["Learning OS"])

# In-memory storage for active quizzes
_ACTIVE_QUIZZES: Dict[str, QuizResponse] = {}


def generate_curriculum(topic: str, goal: str, weeks: int, difficulty: str) -> List[StudyMilestone]:
    """Generates a structured syllabus of study milestones."""
    milestones = []
    base_templates = [
        ("Foundations & Core Principles", f"Understand the fundamental mechanics and key theorems behind {topic}.", ["Definitions", "Mental Models", "History & Context"]),
        ("Architecture & Structural Design", f"Explore component breakdown, interfaces, and patterns in {topic}.", ["System Patterns", "Data Flow", "Separation of Concerns"]),
        ("Practical Implementation & Tooling", f"Hands-on application and building real-world projects with {topic}.", ["Workflow Pipeline", "Debugging", "Performance Tuning"]),
        ("Advanced Optimization & Edge Cases", f"Master edge cases, security, scale, and high-order trade-offs in {topic}.", ["Scale Bottlenecks", "Resilience", "Production Hardening"]),
    ]

    for i in range(min(weeks, len(base_templates))):
        title, desc, concepts = base_templates[i]
        milestones.append(
            StudyMilestone(
                id=f"ms-{i+1}",
                title=f"Week {i+1}: {title}",
                description=desc,
                key_concepts=concepts,
                completed=False,
            )
        )
    return milestones


def build_quiz_for_topic(topic: str, difficulty: str) -> QuizResponse:
    """Builds a verified quiz with multi-choice options and pedagogical explanations."""
    quiz_id = f"quiz-{uuid.uuid4().hex[:8]}"
    questions = [
        QuizQuestion(
            id=1,
            question=f"What is the primary governing principle of {topic}?",
            options=[
                QuizOption(id=0, text="Maximizing unconstrained concurrency without bounds"),
                QuizOption(id=1, text="Deterministic state management and explicit boundaries"),
                QuizOption(id=2, text="Eliminating all procedural abstractions completely"),
                QuizOption(id=3, text="Randomized heuristic selection with no validation"),
            ],
            correct_option_id=1,
            explanation="Rigorous architecture requires deterministic state and strict separation of concerns.",
        ),
        QuizQuestion(
            id=2,
            question=f"When encountering high load or complexity in {topic}, what is the recommended architectural pattern?",
            options=[
                QuizOption(id=0, text="Increasing synchronous call stack depth indefinitely"),
                QuizOption(id=1, text="Asynchronous queuing, decoupled workers, and backpressure"),
                QuizOption(id=2, text="Removing timeouts and error handlers to minimize overhead"),
                QuizOption(id=3, text="Hardcoding thread pools to 1024 fixed workers"),
            ],
            correct_option_id=1,
            explanation="Decoupled queues with backpressure prevent cascade failures under extreme load.",
        ),
        QuizQuestion(
            id=3,
            question=f"In {topic}, how should sensitive state and authorization boundaries be enforced?",
            options=[
                QuizOption(id=0, text="Trusting incoming client metadata without server verification"),
                QuizOption(id=1, text="Applying defense-in-depth with least privilege policy enforcement"),
                QuizOption(id=2, text="Encrypting data only after persistent disk write is finished"),
                QuizOption(id=3, text="Disabling audit logging to conserve system IOPS"),
            ],
            correct_option_id=1,
            explanation="Zero-trust security requires continuous verification and least privilege policies.",
        ),
    ]

    response = QuizResponse(
        id=quiz_id,
        topic=topic,
        difficulty=difficulty,
        questions=questions,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    _ACTIVE_QUIZZES[quiz_id] = response
    return response


DEFAULT_FLASHCARDS = [
    FlashcardItem(
        id="fc-1",
        deck="Distributed Systems",
        front="What does the CAP Theorem state?",
        back="A distributed data store can simultaneously provide at most two out of three guarantees: Consistency, Availability, and Partition Tolerance.",
        mastery_level=2,
    ),
    FlashcardItem(
        id="fc-2",
        deck="AI Architectures",
        front="What is Reciprocal Rank Fusion (RRF)?",
        back="An algorithm that scores documents across different retrieval lists (e.g. dense vectors + lexical BM25) by summing 1 / (60 + rank).",
        mastery_level=3,
    ),
    FlashcardItem(
        id="fc-3",
        deck="Zero-Trust Security",
        front="What is the Principle of Least Privilege?",
        back="Every module or user should have access only to the minimum set of resources and actions strictly necessary to perform its legitimate function.",
        mastery_level=4,
    ),
]


@router.post("/plans", response_model=StudyPlanResponse)
async def create_study_plan(
    payload: StudyPlanCreate,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    """Generates an adaptive study plan with progression milestones."""
    col = db_manager.get_collection("study_plans")
    user_id = user["id"] if user else "default"
    plan_id = f"plan-{uuid.uuid4().hex[:10]}"
    now_iso = datetime.now(timezone.utc).isoformat()

    milestones = generate_curriculum(
        payload.topic,
        payload.target_role_or_goal or "Mastery",
        payload.timeframe_weeks,
        payload.difficulty_level,
    )

    doc = {
        "id": plan_id,
        "user_id": user_id,
        "topic": payload.topic,
        "goal": payload.target_role_or_goal or "Mastery",
        "difficulty_level": payload.difficulty_level,
        "timeframe_weeks": payload.timeframe_weeks,
        "milestones": [m.model_dump() for m in milestones],
        "progress_percent": 0.0,
        "created_at": now_iso,
        "updated_at": now_iso,
    }

    await col.insert_one(doc)
    doc.pop("_id", None)
    return doc


@router.get("/plans", response_model=List[StudyPlanResponse])
async def list_study_plans(
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    """Lists study plans for the user."""
    col = db_manager.get_collection("study_plans")
    user_id = user["id"] if user else "default"
    docs = await col.find({"$or": [{"user_id": user_id}, {"user_id": "default"}]})
    
    # If empty, create default plan
    if not docs:
        default_payload = StudyPlanCreate(
            topic="Modern AI Operating Systems & Autonomous Agents",
            target_role_or_goal="Principal Systems Architect",
            difficulty_level="Advanced",
            timeframe_weeks=4,
        )
        default_plan = await create_study_plan(default_payload, user)
        return [default_plan]

    for d in docs:
        d.pop("_id", None)
    return docs


@router.post("/quiz/generate", response_model=QuizResponse)
async def generate_quiz(
    req: QuizGenerateRequest,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    """Generates an interactive diagnostic quiz."""
    return build_quiz_for_topic(req.topic, req.difficulty)


@router.post("/quiz/submit", response_model=QuizSubmissionResult)
async def submit_quiz(
    sub: QuizSubmissionRequest,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    """Evaluates student quiz submissions with immediate rationale."""
    quiz = _ACTIVE_QUIZZES.get(sub.quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz session expired or not found.")

    correct_count = 0
    results: List[QuizQuestionResult] = []

    for q in quiz.questions:
        user_ans = sub.answers.get(q.id)
        is_corr = (user_ans == q.correct_option_id)
        if is_corr:
            correct_count += 1
        results.append(
            QuizQuestionResult(
                question_id=q.id,
                user_answer=user_ans,
                correct_answer=q.correct_option_id,
                is_correct=is_corr,
                explanation=q.explanation,
            )
        )

    score_pct = round((correct_count / len(quiz.questions)) * 100, 1)
    passed = score_pct >= 70.0

    return QuizSubmissionResult(
        quiz_id=sub.quiz_id,
        total_questions=len(quiz.questions),
        correct_count=correct_count,
        score_percent=score_pct,
        passed=passed,
        results=results,
    )


@router.get("/flashcards", response_model=List[FlashcardItem])
async def get_flashcards(
    deck: Optional[str] = None,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    """Returns flashcards for spaced repetition."""
    if deck:
        return [fc for fc in DEFAULT_FLASHCARDS if fc.deck.lower() == deck.lower()]
    return DEFAULT_FLASHCARDS


@router.post("/socratic/ask", response_model=SocraticResponse)
async def ask_socratic_tutor(
    req: SocraticPromptRequest,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    """Engages the learner via Socratic questioning rather than giving answers directly."""
    student_text = req.student_statement.lower()

    if "why" in student_text or "how" in student_text:
        question = (
            f"Interesting hypothesis about {req.topic}. If you trace what happens to memory or state "
            f"when this condition occurs, what failure mode would emerge first?"
        )
        prompt = "Consider the trade-off between latency and consistency."
        hint = "Think about what happens if a node crashes before acknowledging the transaction."
    else:
        question = (
            f"You mentioned that '{req.student_statement}'. What assumptions are you making about {req.topic} "
            f"and what would happen if the input scale increased by 10,000x?"
        )
        prompt = "Break down the computational complexity and resource boundaries."
        hint = "Recall the difference between O(n) scan vs O(log n) indexing."

    return SocraticResponse(
        coaching_question=question,
        thought_prompt=prompt,
        hint=hint,
    )
