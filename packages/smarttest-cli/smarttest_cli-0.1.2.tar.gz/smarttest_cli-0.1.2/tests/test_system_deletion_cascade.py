import sys
import os
from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure project modules are importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.model import Base, SystemDB, EndpointDB, ScenarioDB  # noqa: E402
from service.SystemService import delete_system  # noqa: E402


@pytest.fixture
def db_session() -> Generator:
    """Provide an in-memory SQLite session for isolated testing."""
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


def test_delete_system_cascades_to_endpoints_and_scenarios(db_session):
    """Deleting a system via SystemService.delete_system should remove endpoints and scenarios."""
    # Arrange: create system with one endpoint and one scenario
    system = SystemDB(name="S", base_url="http://x")
    endpoint = EndpointDB(method="GET", endpoint="/a", raw_definition={}, configured=False)
    scenario = ScenarioDB(name="Scenario 1", endpoint=endpoint)
    endpoint.scenarios.append(scenario)
    system.endpoints.append(endpoint)

    db_session.add(system)
    db_session.commit()

    # Sanity checks
    assert db_session.query(SystemDB).count() == 1
    assert db_session.query(EndpointDB).count() == 1
    assert db_session.query(ScenarioDB).count() == 1

    # Act: delete the system via service (should cascade)
    assert delete_system(db_session, system.id, user_id="user_1") is True

    # Assert: everything cascaded away
    assert db_session.query(SystemDB).count() == 0
    assert db_session.query(EndpointDB).count() == 0
    assert db_session.query(ScenarioDB).count() == 0




