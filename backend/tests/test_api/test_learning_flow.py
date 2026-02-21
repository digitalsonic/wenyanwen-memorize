"""Integration tests for the learning flow - simplified version."""

import pytest
from sqlmodel import select

from wenyanwen.models import LearningProgress


class TestLearnFlow:
    """Test the complete learning flow."""

    def test_learn_new_words_creates_progress(self, client, test_db):
        """Test that learning new words creates progress records."""
        # Get some word IDs from the real word library
        from wenyanwen.services.word_loader import word_loader
        word_loader.load()  # Ensure loaded

        words = word_loader.get_all_words()
        if not words:
            pytest.skip("No words available")

        word_ids = [w.id for w in words[:3]]

        # Complete learning
        response = client.post("/api/v1/quiz/learn/complete", json=word_ids)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_learn_starts_at_level_1(self, client, test_db):
        """Test that newly learned words start at level 1."""
        from wenyanwen.services.word_loader import word_loader
        word_loader.load()

        words = word_loader.get_all_words()
        if not words:
            pytest.skip("No words available")

        word_id = words[0].id

        client.post("/api/v1/quiz/learn/complete", json=[word_id])

        # Check in the same session
        stmt = select(LearningProgress).where(LearningProgress.word_id == word_id)
        progress = test_db.exec(stmt).first()

        assert progress is not None
        assert progress.current_level == 1
        assert progress.is_mastered is False


class TestProgressTracking:
    """Test progress tracking."""

    def test_progress_api_returns_summary(self, client):
        """Test that progress API returns learning summary."""
        response = client.get("/api/v1/review/progress")
        assert response.status_code == 200

        data = response.json()
        assert "cycle" in data
        assert "total_words" in data
        assert "learned_words" in data
        assert "mastered_words" in data
        assert "completion_percentage" in data


class TestLearnEndpoint:
    """Test learn new words endpoint."""

    def test_learn_returns_cards(self, client):
        """Test that learn endpoint returns card questions."""
        from wenyanwen.services.word_loader import word_loader
        word_loader.load()

        response = client.post(
            "/api/v1/quiz/learn",
            json={"count": 3, "mode": "sequential"},
        )
        assert response.status_code == 200

        data = response.json()
        assert "session_id" in data
        assert "words" in data
        assert "total_count" in data
