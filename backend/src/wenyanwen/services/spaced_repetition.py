"""Spaced repetition algorithm implementation (Ebbinghaus forgetting curve)."""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Literal

from sqlmodel import select

if TYPE_CHECKING:
    from sqlmodel import Session

# Level definitions
# Level 0: New word (just learned with card)
# Level 1-6: Review levels with day-based intervals
ReviewLevel = Literal[0, 1, 2, 3, 4, 5, 6]

# Day-level intervals for review (matching Ebbinghaus curve)
INTERVALS: dict[ReviewLevel, timedelta] = {
    1: timedelta(days=1),    # 1st review: 1 day
    2: timedelta(days=2),    # 2nd review: 2 days
    3: timedelta(days=4),    # 3rd review: 4 days
    4: timedelta(days=7),    # 4th review: 7 days
    5: timedelta(days=15),   # 5th review: 15 days
    6: timedelta(days=30),   # 6th review: 30 days (final)
}


def get_quiz_type(level: ReviewLevel) -> str:
    """
    Get the quiz type for a given review level.

    Args:
        level: Current review level

    Returns:
        Quiz type string
    """
    quiz_types = {
        0: "card",             # New word: card mode
        1: "multiple_choice",  # Day 1: multiple choice
        2: "true_false",       # Day 2: true/false
        3: "multiple_choice",  # Day 4: multiple choice
        4: "true_false",       # Day 7: true/false
        5: "multiple_choice",  # Day 15: multiple choice
        6: "flashcard",        # Day 30: flashcard + multiple choice
    }
    return quiz_types.get(level, "multiple_choice")


def calculate_next_review(
    current_level: ReviewLevel = 0,
    is_correct: bool = True,
) -> tuple[datetime | None, ReviewLevel, bool]:
    """
    Calculate the next review time based on performance.

    Args:
        current_level: Current mastery level (0-6)
        is_correct: Whether the user answered correctly

    Returns:
        Tuple of (next_review_time, new_level, is_mastered)
        - next_review_time: None if mastered, otherwise datetime
        - new_level: The new level after this review
        - is_mastered: True if the word is mastered (reached level 6 and answered correctly)
    """
    if is_correct:
        # Correct answer: increase level
        new_level = min(6, current_level + 1)
        # Check if mastered (reached level 6)
        is_mastered = (new_level == 6 and current_level == 6) or (current_level == 6)
    else:
        # Wrong answer: downgrade level 6 to 5 for re-consolidation, others stay at current level
        # Level 6 drops to 5 to force re-testing with objective quiz types
        new_level = max(5, current_level - 1) if current_level == 6 else current_level
        is_mastered = False

    # Calculate next review time
    if is_mastered:
        next_review = None
    elif new_level == 0:
        # Should not happen in normal flow, but handle it
        next_review = datetime.now() + INTERVALS[1]
    else:
        next_review = datetime.now() + INTERVALS[new_level]

    return next_review, new_level, is_mastered


def is_due_for_review(next_review_at: datetime | None) -> bool:
    """
    Check if an item is due for review.

    Args:
        next_review_at: Scheduled review time

    Returns:
        True if due for review, False otherwise
    """
    if next_review_at is None:
        return False  # Mastered words don't need review
    return datetime.now() >= next_review_at


def get_level_name(level: ReviewLevel) -> str:
    """
    Get a human-readable name for the level.

    Args:
        level: Current review level

    Returns:
        Human-readable level name
    """
    level_names = {
        1: "等待第1次复习",
        2: "等待第2次复习",
        3: "等待第3次复习",
        4: "等待第4次复习",
        5: "等待第5次复习",
        6: "等待第6次复习",
    }
    return level_names.get(level, f"等待第{level}次复习")


def get_current_cycle(session: "Session", user_id: int) -> int:
    """
    Get the current learning cycle for a user.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        Current cycle number (1 if no progress exists)
    """
    from ..models import LearningProgress

    all_progress = session.exec(
        select(LearningProgress).where(LearningProgress.user_id == user_id)
    ).all()
    return 1 if not all_progress else max(p.cycle for p in all_progress)
