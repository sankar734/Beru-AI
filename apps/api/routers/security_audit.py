import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from apps.api.auth import get_optional_user
from services.security.audit_ledger import audit_ledger, AuditEntry
from services.security.key_vault import key_vault, KeyMetadata

logger = logging.getLogger("nova.api.security_audit")

router = APIRouter(prefix="/security", tags=["Security Hardening & Audit"])

class RotateKeyRequest(BaseModel):
    key_id: str

class RedactTextRequest(BaseModel):
    text: str

class RedactTextResponse(BaseModel):
    original_length: int
    redacted_text: str
    redactions_made: bool

class ChainIntegrityResponse(BaseModel):
    is_valid: bool
    blocks_count: int
    message: str

@router.get("/audit-trail", response_model=List[AuditEntry])
async def get_audit_trail(limit: int = 50, user: Optional[dict] = Depends(get_optional_user)):
    """Retrieves recent cryptographically verified audit ledger entries."""
    return audit_ledger.get_entries(limit=limit)

@router.post("/verify-integrity", response_model=ChainIntegrityResponse)
async def verify_audit_chain_integrity(user: Optional[dict] = Depends(get_optional_user)):
    """Verifies SHA-256 cryptographic hash-chain across all recorded actions to detect tampering."""
    is_valid, msg = audit_ledger.verify_integrity()
    return ChainIntegrityResponse(
        is_valid=is_valid,
        blocks_count=audit_ledger.get_chain_length(),
        message=msg or ""
    )

@router.get("/vault/keys", response_model=List[KeyMetadata])
async def list_vault_keys(user: Optional[dict] = Depends(get_optional_user)):
    """Lists managed cryptographic keys, rotation age, and safe previews."""
    return key_vault.list_keys_metadata()

@router.post("/vault/rotate", response_model=KeyMetadata)
async def rotate_vault_key(req: RotateKeyRequest, user: Optional[dict] = Depends(get_optional_user)):
    """Performs zero-downtime rotation on a managed secret key and logs to audit ledger."""
    try:
        actor = user.get("email", "security_operator") if user else "security_operator"
        return key_vault.rotate_key(req.key_id, actor=actor)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/redact", response_model=RedactTextResponse)
async def redact_sensitive_text(req: RedactTextRequest, user: Optional[dict] = Depends(get_optional_user)):
    """Sanitizes text by masking OpenAI API keys, GitHub tokens, AWS credentials, and JWTs."""
    sanitized = key_vault.mask_credentials(req.text)
    return RedactTextResponse(
        original_length=len(req.text),
        redacted_text=sanitized,
        redactions_made=sanitized != req.text
    )
