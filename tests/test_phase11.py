import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_study_plan_creation_and_listing():
    payload = {
        "topic": "High-Performance Rust Systems Programming",
        "target_role_or_goal": "Lead Systems Engineer",
        "difficulty_level": "Advanced",
        "timeframe_weeks": 4,
    }
    create_res = client.post("/api/v1/learning/plans", json=payload)
    assert create_res.status_code == 200
    plan = create_res.json()
    assert plan["topic"] == "High-Performance Rust Systems Programming"
    assert len(plan["milestones"]) == 4
    assert "Foundations" in plan["milestones"][0]["title"]

    list_res = client.get("/api/v1/learning/plans")
    assert list_res.status_code == 200
    plans = list_res.json()
    assert len(plans) >= 1
    assert any(p["id"] == plan["id"] for p in plans)


def test_quiz_generation_and_submission():
    # 1. Generate Quiz
    gen_payload = {
        "topic": "Distributed Consensus & Raft",
        "difficulty": "Intermediate",
        "num_questions": 3,
    }
    gen_res = client.post("/api/v1/learning/quiz/generate", json=gen_payload)
    assert gen_res.status_code == 200
    quiz = gen_res.json()
    quiz_id = quiz["id"]
    assert len(quiz["questions"]) == 3
    assert quiz["questions"][0]["options"][1]["text"] != ""

    # 2. Submit Quiz with correct answers (correct option is 1 for all generated questions)
    sub_payload = {
        "quiz_id": quiz_id,
        "answers": {1: 1, 2: 1, 3: 1},
    }
    sub_res = client.post("/api/v1/learning/quiz/submit", json=sub_payload)
    assert sub_res.status_code == 200
    result = sub_res.json()
    assert result["total_questions"] == 3
    assert result["correct_count"] == 3
    assert result["score_percent"] == 100.0
    assert result["passed"] is True
    assert len(result["results"]) == 3


def test_socratic_tutor_and_flashcards():
    # 1. Socratic Coach
    soc_payload = {
        "topic": "Eventual Consistency",
        "student_statement": "I think eventual consistency means all nodes update immediately.",
    }
    soc_res = client.post("/api/v1/learning/socratic/ask", json=soc_payload)
    assert soc_res.status_code == 200
    soc_data = soc_res.json()
    assert "coaching_question" in soc_data
    assert "thought_prompt" in soc_data

    # 2. Flashcards
    fc_res = client.get("/api/v1/learning/flashcards")
    assert fc_res.status_code == 200
    cards = fc_res.json()
    assert len(cards) >= 3
    assert any(c["deck"] == "Distributed Systems" for c in cards)
