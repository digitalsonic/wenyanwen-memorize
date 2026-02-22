"""Unit tests for reset progress endpoint."""

import pytest
from sqlmodel import select

from wenyanwen.models import LearningProgress


class TestResetProgress:
    """Test reset progress endpoint."""

    def test_reset_progress_deletes_created_records(self, client, test_db):
        """Test that reset progress deletes created records."""
        from wenyanwen.services.word_loader import word_loader
        word_loader.load()

        words = word_loader.get_all_words()
        if not words:
            pytest.skip("No words available")

        # Create progress records
        word_ids = [w.id for w in words[:3]]
        for word_id in word_ids:
            progress = LearningProgress(
                user_id=1,
                word_id=word_id,
                cycle=1,
                current_level=2,
                error_count=0,
                is_mastered=False,
            )
            test_db.add(progress)
        test_db.commit()

        # Verify records exist
        stmt = select(LearningProgress).where(
            LearningProgress.user_id == 1,
            LearningProgress.cycle == 1,
        )
        records_before = list(test_db.exec(stmt).all())
        initial_count = len(records_before)
        assert initial_count >= 3

        # Reset progress
        response = client.post("/api/v1/review/reset-progress")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["data"]["deleted_count"] >= 3

        # Verify records are deleted
        records_after = list(test_db.exec(stmt).all())
        assert len(records_after) == 0
