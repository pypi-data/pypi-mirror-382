import time
from pathlib import Path

import pytest

from token_limit_guard import TokenLimitGuard


def test_load_tokens_from_list_and_lru_behavior():
    guard = TokenLimitGuard(["A", "B", "C"])
    guard.set_limiting_factors(max_allowed_count=2, time_window_in_sec=1)

    first = guard.get_a_token()
    second = guard.get_a_token()
    third = guard.get_a_token()

    assert {first, second, third} == {"A", "B", "C"}
    # After all tokens used once, the least recently used should be the earliest.
    lru_order = guard.get_tokens_snapshot()
    assert lru_order[0] == first


def test_non_blocking_returns_none_when_exhausted():
    guard = TokenLimitGuard(["only"])
    guard.set_limiting_factors(max_allowed_count=1, time_window_in_sec=10)

    assert guard.get_a_token() == "only"
    assert guard.get_a_token(block=False) is None
    assert guard.try_get_a_token() is None


def test_blocking_waits_until_token_available(monkeypatch):
    guard = TokenLimitGuard(["rate-limited"])
    guard.set_limiting_factors(max_allowed_count=1, time_window_in_sec=0.2)

    assert guard.get_a_token() == "rate-limited"

    start = time.monotonic()
    next_token = guard.get_a_token(wake_interval=0.01)
    elapsed = time.monotonic() - start

    assert next_token == "rate-limited"
    assert elapsed >= 0.1
    assert elapsed == pytest.approx(0.2, rel=0.5)


def test_loading_tokens_from_file(tmp_path: Path):
    token_file = tmp_path / "tokens.txt"
    token_file.write_text("token1\ntoken2\n", encoding="utf-8")

    guard = TokenLimitGuard(token_file)
    guard.set_limiting_factors(max_allowed_count=1, time_window_in_sec=1)

    assert guard.get_a_token() in {"token1", "token2"}
