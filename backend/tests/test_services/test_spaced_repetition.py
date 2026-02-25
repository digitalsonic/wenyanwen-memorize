"""Unit tests for spaced repetition algorithm."""

import pytest
from datetime import datetime, timedelta

from wenyanwen.services.spaced_repetition import (
    INTERVALS,
    calculate_next_review,
    get_quiz_type,
    get_level_name,
    is_due_for_review,
)


class TestIntervals:
    """Test interval definitions."""

    def test_intervals_are_day_based(self):
        """Test that intervals are defined in days."""
        assert INTERVALS[1] == timedelta(days=1)
        assert INTERVALS[2] == timedelta(days=2)
        assert INTERVALS[3] == timedelta(days=4)
        assert INTERVALS[4] == timedelta(days=7)
        assert INTERVALS[5] == timedelta(days=15)
        assert INTERVALS[6] == timedelta(days=30)

    def test_intervals_increase_with_level(self):
        """Test that intervals increase as level increases."""
        for i in range(1, 6):
            assert INTERVALS[i] < INTERVALS[i + 1]


class TestCalculateNextReview:
    """Test next review calculation."""

    def test_correct_answer_increases_level(self):
        """Test that correct answer increases level."""
        next_review, new_level, is_mastered = calculate_next_review(
            current_level=1,
            is_correct=True,
        )
        assert new_level == 2
        assert not is_mastered
        assert next_review is not None

    def test_correct_answer_at_level_5_masters(self):
        """Test that correct answer at level 5 moves to level 6."""
        next_review, new_level, is_mastered = calculate_next_review(
            current_level=5,
            is_correct=True,
        )
        assert new_level == 6
        assert not is_mastered  # Level 6 still needs one more correct

    def test_correct_answer_at_level_6_masters(self):
        """Test that correct answer at level 6 marks as mastered."""
        next_review, new_level, is_mastered = calculate_next_review(
            current_level=6,
            is_correct=True,
        )
        assert new_level == 6
        assert is_mastered
        assert next_review is None  # No next review for mastered words

    def test_wrong_answer_keeps_level(self):
        """Test that wrong answer keeps the same level."""
        next_review, new_level, is_mastered = calculate_next_review(
            current_level=3,
            is_correct=False,
        )
        assert new_level == 3  # Level unchanged
        assert not is_mastered
        assert next_review is not None  # Still has next review

    def test_wrong_answer_at_level_6_downgrades_to_5(self):
        """Test that wrong answer at level 6 downgrades to level 5 for re-consolidation."""
        next_review, new_level, is_mastered = calculate_next_review(
            current_level=6,
            is_correct=False,
        )
        assert new_level == 5  # Downgrade to level 5
        assert not is_mastered
        assert next_review is not None  # Has next review (15 days)

    def test_correct_answer_at_level_6_stays_mastered(self):
        """Test that correct answer at level 6 keeps mastered status."""
        next_review, new_level, is_mastered = calculate_next_review(
            current_level=6,
            is_correct=True,
        )
        assert new_level == 6  # Stay at level 6
        assert is_mastered
        assert next_review is None  # No next review for mastered words

    def test_wrong_answer_resets_error_count_track(self):
        """Test that wrong answer allows retry at same level."""
        _, new_level, _ = calculate_next_review(
            current_level=2,
            is_correct=False,
        )
        assert new_level == 2  # Stay at level 2

    def test_from_new_to_level_1(self):
        """Test transition from level 0 (new) to level 1."""
        next_review, new_level, is_mastered = calculate_next_review(
            current_level=0,
            is_correct=True,
        )
        assert new_level == 1
        assert not is_mastered
        assert next_review is not None


class TestGetQuizType:
    """Test quiz type mapping."""

    def test_level_0_is_card(self):
        """Test that level 0 (new) uses card type."""
        assert get_quiz_type(0) == "card"

    def test_level_1_is_multiple_choice(self):
        """Test that level 1 uses multiple choice."""
        assert get_quiz_type(1) == "multiple_choice"

    def test_level_2_is_true_false(self):
        """Test that level 2 uses true/false."""
        assert get_quiz_type(2) == "true_false"

    def test_level_3_is_multiple_choice(self):
        """Test that level 3 uses multiple choice."""
        assert get_quiz_type(3) == "multiple_choice"

    def test_level_4_is_true_false(self):
        """Test that level 4 uses true/false."""
        assert get_quiz_type(4) == "true_false"

    def test_level_5_is_multiple_choice(self):
        """Test that level 5 uses multiple choice."""
        assert get_quiz_type(5) == "multiple_choice"

    def test_level_6_is_flashcard(self):
        """Test that level 30 uses flashcard."""
        assert get_quiz_type(6) == "flashcard"


class TestGetLevelName:
    """Test level name mapping."""

    def test_level_names(self):
        """Test that level names are correct."""
        assert get_level_name(1) == "等待第1次复习"
        assert get_level_name(2) == "等待第2次复习"
        assert get_level_name(3) == "等待第3次复习"
        assert get_level_name(4) == "等待第4次复习"
        assert get_level_name(5) == "等待第5次复习"
        assert get_level_name(6) == "等待第6次复习"
        # Level 0 is not used in practice (no progress records at level 0)
        assert get_level_name(0) == "等待第0次复习"


class TestIsDueForReview:
    """Test due check."""

    def test_past_time_is_due(self):
        """Test that past time is due."""
        past = datetime.now() - timedelta(hours=1)
        assert is_due_for_review(past) is True

    def test_future_time_is_not_due(self):
        """Test that future time is not due."""
        future = datetime.now() + timedelta(hours=1)
        assert is_due_for_review(future) is False

    def test_none_is_not_due(self):
        """Test that None (mastered) is not due."""
        assert is_due_for_review(None) is False

    def test_current_time_is_due(self):
        """Test that current time is due."""
        now = datetime.now()
        assert is_due_for_review(now) is True
