import pytest
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.model import Base, Customer
from service.SubscriptionService import SubscriptionService


@pytest.fixture
def db_session():
    """Create isolated in-memory DB session for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def _create_customer(db, customer_id: str = "user_1") -> Customer:
    customer = Customer(id=customer_id, email=f"{customer_id}@example.com", first_name="T", last_name="U")
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def test_ensure_customer_has_subscription_creates_free_when_missing(db_session):
    """
    When a customer has no subscription, ensure_customer_has_subscription should create
    a subscription on the free tier (creating the tier if needed).
    """
    customer = _create_customer(db_session, "cust_free_new")

    # No tiers/subscriptions exist initially
    sub = SubscriptionService.ensure_customer_has_subscription(db_session, customer.id)

    assert sub is not None
    assert sub.customer_id == customer.id
    assert sub.status == "active"
    # Free tier must be created/linked
    assert sub.tier is not None
    assert sub.tier.name == "free"

    # get_usage_limits should now work and compute defaults from free tier
    limits = SubscriptionService.get_usage_limits(db_session, customer.id)
    assert limits is not None
    assert limits.subscription.tier.name == "free"
    # By default no usage yet
    assert limits.runs_used == 0
    assert limits.scenarios_used == 0


def test_ensure_customer_has_subscription_is_idempotent(db_session):
    """
    Calling ensure_customer_has_subscription twice should return the same active
    subscription and not create duplicates.
    """
    customer = _create_customer(db_session, "cust_idem")

    first = SubscriptionService.ensure_customer_has_subscription(db_session, customer.id)
    second = SubscriptionService.ensure_customer_has_subscription(db_session, customer.id)

    assert first.id == second.id
    # Only one active subscription should exist for this customer
    from database.model import CustomerSubscription

    active_count = (
        db_session.query(CustomerSubscription)
        .filter(CustomerSubscription.customer_id == customer.id, CustomerSubscription.status == "active")
        .count()
    )
    assert active_count == 1


