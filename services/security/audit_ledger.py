import time
import json
import hashlib
import logging
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

logger = logging.getLogger("nova.security.audit")

class AuditEntry(BaseModel):
    entry_id: int
    timestamp: float = Field(default_factory=time.time)
    action: str
    actor: str = "system"
    risk_level: int = 1
    details: Dict[str, Any] = Field(default_factory=dict)
    prev_hash: str
    entry_hash: str

class AuditLedger:
    """
    Append-only cryptographically chained audit trail.
    Uses SHA-256 hash chaining to ensure tamper-evidence across all actions.
    """

    GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    def __init__(self):
        self._chain: List[AuditEntry] = []
        self._init_genesis()

    def _init_genesis(self):
        genesis_entry = self._create_entry(
            entry_id=0,
            action="GENESIS_SYSTEM_INITIALIZATION",
            actor="nova-kernel",
            risk_level=0,
            details={"version": "1.0.0", "platform": "NOVA X Personal Intelligence OS"},
            prev_hash=self.GENESIS_HASH
        )
        self._chain.append(genesis_entry)

    def _compute_hash(
        self,
        entry_id: int,
        timestamp: float,
        action: str,
        actor: str,
        risk_level: int,
        details: Dict[str, Any],
        prev_hash: str
    ) -> str:
        payload = f"{prev_hash}:{entry_id}:{timestamp:.4f}:{action}:{actor}:{risk_level}:{json.dumps(details, sort_keys=True)}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _create_entry(
        self,
        entry_id: int,
        action: str,
        actor: str,
        risk_level: int,
        details: Dict[str, Any],
        prev_hash: str
    ) -> AuditEntry:
        now = time.time()
        entry_hash = self._compute_hash(entry_id, now, action, actor, risk_level, details, prev_hash)
        return AuditEntry(
            entry_id=entry_id,
            timestamp=now,
            action=action,
            actor=actor,
            risk_level=risk_level,
            details=details,
            prev_hash=prev_hash,
            entry_hash=entry_hash
        )

    def append(
        self,
        action: str,
        actor: str = "operator",
        risk_level: int = 1,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditEntry:
        """Appends a new immutable verified record to the cryptographic chain."""
        details_dict = details or {}
        last_entry = self._chain[-1]
        next_id = len(self._chain)
        new_entry = self._create_entry(
            entry_id=next_id,
            action=action,
            actor=actor,
            risk_level=risk_level,
            details=details_dict,
            prev_hash=last_entry.entry_hash
        )
        self._chain.append(new_entry)
        return new_entry

    def verify_integrity(self) -> tuple[bool, Optional[str]]:
        """
        Validates cryptographic integrity of the entire audit chain.
        Returns (True, None) if completely verified, or (False, error_message) if tampered.
        """
        if not self._chain:
            return False, "Audit ledger is empty"

        # Check genesis
        if self._chain[0].prev_hash != self.GENESIS_HASH:
            return False, "Genesis block prev_hash is corrupted."

        for i in range(len(self._chain)):
            entry = self._chain[i]

            # 1. Verify prev_hash matches prior entry's hash
            if i > 0:
                prev_entry = self._chain[i - 1]
                if entry.prev_hash != prev_entry.entry_hash:
                    return False, f"Broken link at block #{entry.entry_id}: prev_hash does not match #{prev_entry.entry_id} hash."

            # 2. Recalculate hash to detect content mutation
            recomputed = self._compute_hash(
                entry.entry_id,
                entry.timestamp,
                entry.action,
                entry.actor,
                entry.risk_level,
                entry.details,
                entry.prev_hash
            )
            if entry.entry_hash != recomputed:
                return False, f"Tamper detected in block #{entry.entry_id}: content hash does not match signature."

        return True, f"Verified {len(self._chain)} blocks without corruption."

    def get_entries(self, limit: int = 50) -> List[AuditEntry]:
        """Returns recent audit entries in reverse chronological order."""
        return list(reversed(self._chain[-limit:]))

    def get_chain_length(self) -> int:
        return len(self._chain)

audit_ledger = AuditLedger()
