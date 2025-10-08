from datetime import datetime
from types import SimpleNamespace

from sqlalchemy.orm import Session

from service.SubscriptionService import SubscriptionService


def _mk_subscription(start_iso: str, billing_cycle: str = "monthly", tier_name: str = "starter"):
    started_at = datetime.fromisoformat(start_iso)
    # Minimal subscription namespace that service expects
    return SimpleNamespace(
        customer_id="u1",
        id=1,
        started_at=started_at,
        billing_cycle=billing_cycle,
        tier=SimpleNamespace(name=tier_name),
    )


def test_monthly_period_anchor_mid_month_forward():
    sub = _mk_subscription("2025-01-15T00:00:00")
    # current time on Feb 20, 2025
    cur = datetime.fromisoformat("2025-02-20T12:00:00")
    start, end = SubscriptionService._compute_monthly_anchored_period(sub.started_at, cur)
    assert start == datetime(2025, 2, 15, 0, 0, 0)
    assert end == datetime(2025, 3, 14, 23, 59, 59)


def test_monthly_period_anchor_before_anchor_day():
    sub = _mk_subscription("2025-01-15T00:00:00")
    # current time on Feb 10 < anchor day
    cur = datetime.fromisoformat("2025-02-10T09:00:00")
    start, end = SubscriptionService._compute_monthly_anchored_period(sub.started_at, cur)
    assert start == datetime(2025, 1, 15, 0, 0, 0)
    assert end == datetime(2025, 2, 14, 23, 59, 59)


def test_monthly_period_handles_short_months_before_anchor():
    # Anchor on 31st; current time before Feb anchor -> period is Jan 31 to Feb 27
    sub = _mk_subscription("2025-01-31T00:00:00")
    cur = datetime.fromisoformat("2025-02-20T12:00:00")
    start, end = SubscriptionService._compute_monthly_anchored_period(sub.started_at, cur)
    assert start == datetime(2025, 1, 31, 0, 0, 0)
    assert end == datetime(2025, 2, 27, 23, 59, 59)


def test_monthly_period_handles_short_months_after_anchor():
    # Anchor on 31st; current time after Feb anchor -> period is Feb 28 to Mar 30
    sub = _mk_subscription("2025-01-31T00:00:00")
    cur = datetime.fromisoformat("2025-03-01T00:00:00")
    start, end = SubscriptionService._compute_monthly_anchored_period(sub.started_at, cur)
    assert start == datetime(2025, 2, 28, 0, 0, 0)
    assert end == datetime(2025, 3, 30, 23, 59, 59)


def test_yearly_period_anchor_forward():
    sub = _mk_subscription("2023-06-10T00:00:00", billing_cycle="yearly")
    cur = datetime.fromisoformat("2025-08-01T00:00:00")
    start, end = SubscriptionService._compute_yearly_anchored_period(sub.started_at, cur)
    assert start == datetime(2025, 6, 10, 0, 0, 0)
    assert end == datetime(2026, 6, 9, 23, 59, 59)


def test_yearly_period_anchor_before_anniversary():
    sub = _mk_subscription("2023-06-10T00:00:00", billing_cycle="yearly")
    cur = datetime.fromisoformat("2025-05-01T00:00:00")
    start, end = SubscriptionService._compute_yearly_anchored_period(sub.started_at, cur)
    assert start == datetime(2024, 6, 10, 0, 0, 0)
    assert end == datetime(2025, 6, 9, 23, 59, 59)


