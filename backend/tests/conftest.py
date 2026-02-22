"""Pytest configuration and fixtures."""

import os

import pytest
from sqlmodel import Session, create_engine, SQLModel

from wenyanwen.database import get_session

# Ensure we're not using file database in tests
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Test database (in-memory) with check_same_thread disabled for testing
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
)

# Sanity check: fail if test engine is using a file
if test_engine.url.database and test_engine.url.database != ":memory:":
    raise RuntimeError(
        f"Tests must use in-memory database, but got: {test_engine.url.database}"
    )


@pytest.fixture(autouse=True)
def verify_test_database():
    """Verify that tests are not using file database."""
    # Only check if DATABASE_URL env var was explicitly set to something other than memory
    db_url = os.environ.get("DATABASE_URL", "")
    if db_url and not db_url.startswith("sqlite:///:memory:"):
        raise RuntimeError(
            f"Tests must use in-memory database, but DATABASE_URL={db_url}"
    )
    yield


@pytest.fixture
def test_db():
    """Create a test database."""
    SQLModel.metadata.create_all(test_engine)
    session = Session(test_engine)
    try:
        yield session
    finally:
        session.close()
        SQLModel.metadata.drop_all(test_engine)


@pytest.fixture
def client(test_db):
    """Create a test client with a test database."""
    from wenyanwen.main import create_app

    def override_get_session():
        return test_db

    app = create_app()
    app.dependency_overrides[get_session] = override_get_session

    from fastapi.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
