"""Offline deployment check for the established FreshSky budget-lock contract.

Contract source: freshskyai@b682121fc5f02b4b2b74ff1ec508f4116c9dbff9,
budget_runtime.py and tools/check_cloud_run_budget_lock.sh.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import sys


MAX_OPEN_STATE_AGE = timedelta(hours=30)
MAX_OPEN_STATE_FUTURE_SKEW = timedelta(minutes=2)


def is_fresh_open(value: str, *, now: datetime | None = None) -> bool:
    """Accept only timestamped open state within the existing time bounds."""
    raw = value.strip()
    if not raw.startswith("open:"):
        return False
    try:
        opened_at = datetime.fromisoformat(raw.removeprefix("open:").replace("Z", "+00:00"))
    except ValueError:
        return False
    if opened_at.tzinfo is None:
        return False
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    opened_at = opened_at.astimezone(timezone.utc)
    return (
        current - MAX_OPEN_STATE_AGE
        <= opened_at
        <= current + MAX_OPEN_STATE_FUTURE_SKEW
    )


if __name__ == "__main__":
    raise SystemExit(0 if is_fresh_open(sys.stdin.read()) else 1)
