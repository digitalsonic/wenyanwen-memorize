"""Pytest configuration and fixtures."""

import pytest
from sqlmodel import Session, create_engine
from sqlmodel.sql.base import SQLModel

from wenyanwen.database import get_session
from wenyanwen.main import create_app


# Test database (in-memory)
test_engine = create_engine("sqlite:///:memory:")


@pytest.fixture
def test_db():
    """Create a test database."""
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture
def client(test_db):
    """Create a test client with a test database."""
    from wenyanwen import main

    def override_get_session():
        return test_db

    main.app.dependency_overrides[get_session] = override_get_session

    from fastapi.testclient import TestClient

    with TestClient(main.app) as client:
        yield client

    main.app.dependency_overrides.clear()
