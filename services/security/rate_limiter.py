import time
from collections import defaultdict, deque
from typing import Dict, Tuple

class TokenBucketRateLimiter:
    """Sliding window token-bucket rate limiter per IP/client."""

    def __init__(self, default_limit: int = 120, default_window: int = 60):
        self.default_limit = default_limit
        self.default_window = default_window
        self._history: Dict[str, deque] = defaultdict(deque)

    def check_rate_limit(
        self,
        client_id: str,
        limit: int = 120,
        window_seconds: int = 60
    ) -> Tuple[bool, int, int]:
        """
        Evaluates request against sliding window limit.
        Returns: (allowed: bool, remaining: int, retry_after_seconds: int)
        """
        now = time.time()
        window_start = now - window_seconds
        records = self._history[client_id]

        # Evict old timestamps
        while records and records[0] < window_start:
            records.popleft()

        if len(records) >= limit:
            retry_after = max(1, int(records[0] + window_seconds - now))
            return False, 0, retry_after

        records.append(now)
        remaining = limit - len(records)
        return True, remaining, 0

    def reset_client(self, client_id: str):
        if client_id in self._history:
            self._history[client_id].clear()

rate_limiter = TokenBucketRateLimiter()
