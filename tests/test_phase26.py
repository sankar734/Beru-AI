import pytest
from fastapi.testclient import TestClient
from apps.api.main import app
from services.security.rate_limiter import rate_limiter
from services.security.audit_ledger import audit_ledger

client = TestClient(app)

def test_security_hardening_headers():
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.headers.get("x-content-type-options") == "nosniff"
    assert resp.headers.get("x-frame-options") == "DENY"
    assert "mode=block" in resp.headers.get("x-xss-protection", "")
    assert "max-age=" in resp.headers.get("strict-transport-security", "")
    assert "x-ratelimit-remaining" in resp.headers

def test_rate_limiting_enforcement():
    test_client_id = "192.168.1.99"
    rate_limiter.reset_client(test_client_id)

    # Allow up to 3
    for _ in range(3):
        allowed, remaining, _ = rate_limiter.check_rate_limit(test_client_id, limit=3, window_seconds=60)
        assert allowed is True

    # 4th request must be rejected
    allowed, remaining, retry_after = rate_limiter.check_rate_limit(test_client_id, limit=3, window_seconds=60)
    assert allowed is False
    assert remaining == 0
    assert retry_after > 0

    rate_limiter.reset_client(test_client_id)

def test_credential_redaction_engine():
    raw_text = (
        "Leaked keys: OpenAI sk-proj-12345678901234567890123456, "
        "GitHub ghp_abcdefghijklmnopqrstuvwxyz1234567890, "
        "AWS AKIAIOSFODNN7EXAMPLE."
    )
    resp = client.post("/api/v1/security/redact", json={"text": raw_text})
    assert resp.status_code == 200
    data = resp.json()
    assert data["redactions_made"] is True
    assert "[REDACTED_OPENAI_KEY]" in data["redacted_text"]
    assert "[REDACTED_GITHUB_TOKEN]" in data["redacted_text"]
    assert "[REDACTED_AWS_KEY]" in data["redacted_text"]
    assert "sk-proj" not in data["redacted_text"]

def test_key_vault_and_rotation():
    # 1. List keys
    list_resp = client.get("/api/v1/security/vault/keys")
    assert list_resp.status_code == 200
    keys = list_resp.json()
    key_ids = [k["key_id"] for k in keys]
    assert "jwt_primary" in key_ids
    assert "openai_api_key" in key_ids

    # 2. Rotate a key
    rot_resp = client.post("/api/v1/security/vault/rotate", json={"key_id": "jwt_primary"})
    assert rot_resp.status_code == 200
    rot_data = rot_resp.json()
    assert rot_data["rotations_count"] >= 1
    assert rot_data["is_active"] is True

def test_cryptographic_audit_ledger_and_tamper_detection():
    # 1. Verify chain integrity via API
    verify_resp = client.post("/api/v1/security/verify-integrity")
    assert verify_resp.status_code == 200
    data = verify_resp.json()
    assert data["is_valid"] is True
    assert data["blocks_count"] >= 2

    # 2. Verify audit trail retrieval
    trail_resp = client.get("/api/v1/security/audit-trail?limit=10")
    assert trail_resp.status_code == 200
    entries = trail_resp.json()
    assert len(entries) >= 2
    for e in entries:
        assert "entry_hash" in e
        assert "prev_hash" in e

    # 3. Tamper test on ledger block
    original_action = audit_ledger._chain[1].action
    audit_ledger._chain[1].action = "MALICIOUS_TAMPERED_ACTION"
    is_valid, err_msg = audit_ledger.verify_integrity()
    assert is_valid is False
    assert "Tamper detected" in err_msg

    # Restore
    audit_ledger._chain[1].action = original_action
    is_valid_restored, _ = audit_ledger.verify_integrity()
    assert is_valid_restored is True
