"""Pytest configuration and fixtures."""

import pytest
from sqlmodel import Session, create_engine, SQLModel

from wenyanwen.database import get_session


# Test database (in-memory) with check_same_thread disabled for testing
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
)


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
