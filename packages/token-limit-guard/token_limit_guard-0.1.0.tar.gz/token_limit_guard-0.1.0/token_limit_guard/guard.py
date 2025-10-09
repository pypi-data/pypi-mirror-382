"""Core implementation of :class:`TokenLimitGuard`."""
from __future__ import annotations

import logging
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Deque, Iterable, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class _TokenState:
    token: str
    last_used: float = 0.0
    usage_timestamps: Deque[float] = field(default_factory=deque)

    def prune(self, now: float, window: float) -> None:
        """Remove timestamps that fall outside the rolling window."""
        while self.usage_timestamps and now - self.usage_timestamps[0] >= window:
            expired_at = self.usage_timestamps.popleft()
            logger.debug("Pruned usage timestamp %.6f for token '%s'", expired_at, self.token)


class TokenLimitGuard:
    """Provide rate-limited, least-recently-used token access.

    Parameters
    ----------
    source:
        Either a path to a file containing one token per line, or an iterable of
        pre-loaded token strings.
    """

    def __init__(self, source: str | Path | Iterable[str]):
        self._lock = threading.RLock()
        self._max_allowed_count: Optional[int] = None
        self._time_window: Optional[float] = None
        self._tokens = self._load_tokens(source)
        logger.debug("Initialized guard with %d tokens", len(self._tokens))

        if not self._tokens:
            raise ValueError("TokenLimitGuard requires at least one token")

    def _load_tokens(self, source: str | Path | Iterable[str]) -> List[_TokenState]:
        if isinstance(source, (str, Path)):
            path = Path(source)
            if not path.exists():
                raise FileNotFoundError(f"Token file not found: {path}")
            raw_tokens = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
            logger.debug("Loaded %d tokens from file %s", len(raw_tokens), path)
        else:
            raw_tokens = [token.strip() for token in source]
            logger.debug("Loaded %d tokens from iterable", len(raw_tokens))

        unique_tokens = []
        seen = set()
        for token in raw_tokens:
            if not token:
                continue
            if token in seen:
                logger.debug("Skipping duplicate token '%s'", token)
                continue
            seen.add(token)
            unique_tokens.append(_TokenState(token=token))

        return unique_tokens

    def set_limiting_factors(self, *, max_allowed_count: int, time_window_in_sec: int | float) -> None:
        """Configure rate limiting.

        Parameters
        ----------
        max_allowed_count:
            Maximum number of times a single token may be checked out within the
            configured time window.
        time_window_in_sec:
            Rolling time window in seconds.
        """

        if max_allowed_count <= 0:
            raise ValueError("max_allowed_count must be positive")
        if time_window_in_sec <= 0:
            raise ValueError("time_window_in_sec must be positive")

        with self._lock:
            self._max_allowed_count = int(max_allowed_count)
            self._time_window = float(time_window_in_sec)
            logger.info(
                "Set rate limiting to max=%d per %.2f sec", self._max_allowed_count, self._time_window
            )

    def _assert_configured(self) -> None:
        if self._max_allowed_count is None or self._time_window is None:
            raise RuntimeError("Limiting factors must be configured before requesting tokens")

    def _select_available_token(self, now: float) -> Optional[_TokenState]:
        assert self._max_allowed_count is not None
        assert self._time_window is not None

        available: List[_TokenState] = []
        for state in self._tokens:
            state.prune(now, self._time_window)
            if len(state.usage_timestamps) < self._max_allowed_count:
                available.append(state)

        if not available:
            return None

        chosen = min(available, key=lambda item: item.last_used)
        logger.debug("Selected token '%s' with last_used %.6f", chosen.token, chosen.last_used)
        return chosen

    def _calculate_wait_time(self, now: float) -> float:
        assert self._max_allowed_count is not None
        assert self._time_window is not None

        wait_times: List[float] = []
        for state in self._tokens:
            if not state.usage_timestamps:
                continue
            if len(state.usage_timestamps) < self._max_allowed_count:
                wait_times.append(0.0)
                continue
            oldest = state.usage_timestamps[0]
            wait = self._time_window - (now - oldest)
            wait_times.append(max(wait, 0.0))
            logger.debug(
                "Token '%s' fully utilized; earliest availability in %.6f seconds",
                state.token,
                wait_times[-1],
            )

        return max(min(wait_times, default=0.0), 0.0)

    def get_a_token(self, *, block: bool = True, wake_interval: float = 0.1) -> Optional[str]:
        """Retrieve a token respecting configured rate limits.

        Parameters
        ----------
        block:
            When ``True`` (default), wait until a token becomes available. When
            ``False``, return ``None`` immediately if all tokens are exhausted.
        wake_interval:
            When blocking, the frequency in seconds with which the loop rechecks
            availability. This acts as an upper bound on sleep granularity.

        Returns
        -------
        Optional[str]
            A token string, or ``None`` in non-blocking mode when no token is
            available.
        """

        self._assert_configured()

        if wake_interval <= 0:
            raise ValueError("wake_interval must be positive")

        while True:
            with self._lock:
                now = time.monotonic()
                token_state = self._select_available_token(now)
                if token_state is not None:
                    token_state.usage_timestamps.append(now)
                    token_state.last_used = now
                    logger.info("Dispensed token '%s'", token_state.token)
                    return token_state.token

                if not block:
                    logger.debug("No tokens available (non-blocking call)")
                    return None

                wait_time = self._calculate_wait_time(now)
                sleep_duration = max(min(wait_time, wake_interval), wake_interval)
                logger.debug(
                    "All tokens exhausted; sleeping for %.6f seconds (wait_time=%.6f)",
                    sleep_duration,
                    wait_time,
                )

            time.sleep(sleep_duration)

    def try_get_a_token(self) -> Optional[str]:
        """Non-blocking alias for :meth:`get_a_token`."""
        return self.get_a_token(block=False)

    def get_tokens_snapshot(self) -> List[str]:
        """Return the configured tokens in LRU order (least used first)."""
        with self._lock:
            sorted_states = sorted(self._tokens, key=lambda state: state.last_used)
            snapshot = [state.token for state in sorted_states]
            logger.debug("Snapshot of tokens in LRU order: %s", snapshot)
            return snapshot
