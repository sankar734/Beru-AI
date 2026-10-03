import re
import time
import secrets
import logging
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from .audit_ledger import audit_ledger

logger = logging.getLogger("nova.security.vault")

class KeyMetadata(BaseModel):
    key_id: str
    name: str
    algorithm: str = "AES-256-GCM"
    created_at: float = Field(default_factory=time.time)
    last_rotated_at: float = Field(default_factory=time.time)
    rotations_count: int = 0
    is_active: bool = True
    preview: str = ""

class KeyVault:
    """Manages secret credentials, zero-downtime key rotation, and automated credential redaction."""

    def __init__(self):
        self._keys: Dict[str, str] = {}
        self._metadata: Dict[str, KeyMetadata] = {}
        self._init_defaults()

    def _init_defaults(self):
        self._register_initial_key("jwt_primary", "JWT Authentication Secret", secrets.token_hex(32))
        self._register_initial_key("openai_api_key", "OpenAI LLM Provider Token", "sk-nova-" + secrets.token_urlsafe(24))
        self._register_initial_key("github_pat", "GitHub Personal Access Token", "ghp_" + secrets.token_urlsafe(32))

    def _register_initial_key(self, key_id: str, name: str, value: str):
        self._keys[key_id] = value
        preview = f"{value[:6]}...{value[-4:]}" if len(value) > 10 else "***"
        self._metadata[key_id] = KeyMetadata(
            key_id=key_id,
            name=name,
            algorithm="AES-256-GCM",
            created_at=time.time(),
            last_rotated_at=time.time(),
            rotations_count=0,
            preview=preview
        )

    def get_key(self, key_id: str) -> Optional[str]:
        return self._keys.get(key_id)

    def list_keys_metadata(self) -> List[KeyMetadata]:
        return list(self._metadata.values())

    def rotate_key(self, key_id: str, actor: str = "security_admin") -> KeyMetadata:
        """Rotates key secret and appends cryptographic audit trail entry."""
        if key_id not in self._keys:
            raise KeyError(f"Key '{key_id}' not found in vault")

        new_secret = secrets.token_urlsafe(32)
        if key_id.startswith("openai"):
            new_secret = "sk-nova-" + secrets.token_urlsafe(24)
        elif key_id.startswith("github"):
            new_secret = "ghp_" + secrets.token_urlsafe(32)

        self._keys[key_id] = new_secret
        meta = self._metadata[key_id]
        meta.last_rotated_at = time.time()
        meta.rotations_count += 1
        meta.preview = f"{new_secret[:6]}...{new_secret[-4:]}" if len(new_secret) > 10 else "***"

        audit_ledger.append(
            action="SECRET_KEY_ROTATED",
            actor=actor,
            risk_level=3,
            details={
                "key_id": key_id,
                "key_name": meta.name,
                "rotations_count": meta.rotations_count
            }
        )

        return meta

    def mask_credentials(self, text: str) -> str:
        """Sanitizes text by redacting API keys, JWT tokens, AWS keys, and credit cards."""
        if not text:
            return text

        # OpenAI keys: sk-...
        masked = re.sub(r'sk-[a-zA-Z0-9_\-]{20,}', '[REDACTED_OPENAI_KEY]', text)

        # GitHub tokens: ghp_...
        masked = re.sub(r'gh[pousr]_[a-zA-Z0-9]{36,}', '[REDACTED_GITHUB_TOKEN]', masked)

        # AWS Access Key: AKIA...
        masked = re.sub(r'AKIA[0-9A-Z]{16}', '[REDACTED_AWS_KEY]', masked)

        # JWT tokens: eyJ...
        masked = re.sub(r'eyJ[a-zA-Z0-9_\-]+\.eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+', '[REDACTED_JWT]', masked)

        # Credit card numbers
        masked = re.sub(r'\b(?:\d{4}[-\s]?){3}\d{4}\b', '[REDACTED_CARD_NUMBER]', masked)

        return masked

key_vault = KeyVault()
