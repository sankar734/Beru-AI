import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_expert_roster_and_defaults():
    res = client.get("/api/v1/experts")
    assert res.status_code == 200
    experts = res.json()
    assert len(experts) >= 4
    names = [e["name"] for e in experts]
    assert "Alex Vance" in names
    assert "Cipher Zero" in names


def test_create_and_consult_custom_expert():
    # 1. Create Custom Specialist
    create_payload = {
        "name": "Marcus Aurelius",
        "role": "Stoic Executive Leadership Coach",
        "system_prompt": "You view all organizational challenges through ancient Stoic wisdom and virtue ethics.",
        "color_theme": "amber",
        "capabilities": ["Executive Composure", "Ego Deconstruction", "Long-Horizon Strategy"],
        "temperature": 0.2,
    }
    create_res = client.post("/api/v1/experts", json=create_payload)
    assert create_res.status_code == 200
    expert = create_res.json()
    expert_id = expert["id"]
    assert expert["name"] == "Marcus Aurelius"
    assert expert["is_system_default"] is False

    # 2. Consult Specialist
    consult_payload = {
        "query": "A major production outage occurred and team morale is plummeting.",
        "context": "Customer SLA breach imminent.",
    }
    consult_res = client.post(f"/api/v1/experts/{expert_id}/consult", json=consult_payload)
    assert consult_res.status_code == 200
    consult_data = consult_res.json()
    assert consult_data["expert_name"] == "Marcus Aurelius"
    assert len(consult_data["key_recommendations"]) > 0
    assert len(consult_data["suggested_followups"]) > 0

    # 3. Prevent Deletion of System Default
    system_del_res = client.delete("/api/v1/experts/exp-systems-arch")
    assert system_del_res.status_code == 400

    # 4. Delete Custom Expert
    del_res = client.delete(f"/api/v1/experts/{expert_id}")
    assert del_res.status_code == 200
