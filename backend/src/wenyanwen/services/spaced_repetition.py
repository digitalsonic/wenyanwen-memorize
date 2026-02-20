"""Spaced repetition algorithm implementation (Ebbinghaus forgetting curve)."""

from datetime import datetime, timedelta
from typing import Literal


IntervalLevel = Literal[1, 2, 3, 4, 5, 6]


# Ebbinghaus review intervals (in days)
# Based on the standard spaced repetition schedule
INTERVALS: dict[IntervalLevel, timedelta] = {
    1: timedelta(minutes=5),      # First review: 5 minutes
    2: timedelta(hours=1),        # Second review: 1 hour
    3: timedelta(hours=6),        # Third review: 6 hours
    4: timedelta(days=1),         # Fourth review: 1 day
    5: timedelta(days=2),         # Fifth review: 2 days
    6: timedelta(days=4),         # Sixth review: 4 days
}


def calculate_next_review(
    current_level: IntervalLevel = 1,
    is_correct: bool = True,
) -> tuple[datetime, IntervalLevel]:
    """
    Calculate the next review time based on performance.

    Args:
        current_level: Current mastery level (1-6)
        is_correct: Whether the user answered correctly

    Returns:
        Tuple of (next_review_time, new_level)
    """
    if is_correct:
        # Correct answer: increase level
        new_level = min(6, current_level + 1)
    else:
        # Wrong answer: reset to level 1
        new_level = 1

    next_review = datetime.now() + INTERVALS[new_level]
    return next_review, new_level


def is_due_for_review(next_review_at: datetime | None) -> bool:
    """
    Check if an item is due for review.

    Args:
        next_review_at: Scheduled review time

    Returns:
        True if due for review, False otherwise
    """
    if next_review_at is None:
        return True
    return datetime.now() >= next_review_at
