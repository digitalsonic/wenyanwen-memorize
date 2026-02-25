"""Review API endpoints."""

from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ...database import get_session
from ...models import LearningProgress, QuizType
from ...schemas import APIResponse, ReviewItem, ReviewList
from ...services.spaced_repetition import get_level_name, get_quiz_type
from ...services.word_loader import word_loader

router = APIRouter()


@router.get("/list", response_model=ReviewList)
def get_review_list(
    user_id: int = 1,  # TODO: Replace with auth
    session: Session = Depends(get_session),
):
    """
    Get list of items due for review, grouped by level.

    Args:
        user_id: User ID
        session: Database session

    Returns:
        List of review items grouped by level
    """
    # Get all progress records
    stmt = select(LearningProgress).where(
        LearningProgress.user_id == user_id,
        LearningProgress.current_level > 0,
        LearningProgress.is_mastered == False,
    )
    progress_list = session.exec(stmt).all()

    # Filter due items by date (not precise time)
    today = date.today()
    due_items = []

    for progress in progress_list:
        review_date = progress.next_review_at.date() if progress.next_review_at else None
        if review_date is None or review_date <= today:
            word_data = word_loader.get_word_by_id(progress.word_id)
            if not word_data:
                continue

            quiz_type = get_quiz_type(progress.current_level)

            item = ReviewItem(
                word_id=progress.word_id,
                word=word_data.word,
                level=progress.current_level,
                quiz_type=QuizType(quiz_type),
                error_count=progress.error_count,
                last_review_at=progress.last_review_at,
                next_review_at=progress.next_review_at,
                word_data=word_data,
            )
            due_items.append(item)

    # Group by level
    grouped: dict[int, list[ReviewItem]] = {}
    for item in due_items:
        if item.level not in grouped:
            grouped[item.level] = []
        grouped[item.level].append(item)

    return ReviewList(
        items=due_items,
        total_count=len(due_items),
        grouped=grouped,
    )


@router.get("/progress")
def get_learning_progress(
    user_id: int = 1,  # TODO: Replace with auth
    session: Session = Depends(get_session),
):
    """
    Get learning progress summary.

    Args:
        user_id: User ID
        session: Database session

    Returns:
        Learning progress summary
    """
    # Get current cycle
    cycle_stmt = select(LearningProgress).where(
        LearningProgress.user_id == user_id,
    )
    all_progress = session.exec(cycle_stmt).all()

    current_cycle = 1 if not all_progress else max(p.cycle for p in all_progress)

    # Get progress for current cycle
    stmt = select(LearningProgress).where(
        LearningProgress.user_id == user_id,
        LearningProgress.cycle == current_cycle,
    )
    progress_list = session.exec(stmt).all()

    total_words = word_loader.total_count
    learned_words = len([p for p in progress_list if p.current_level > 0])
    mastered_words = len([p for p in progress_list if p.is_mastered])

    # Count by level
    level_counts: dict[int, int] = dict.fromkeys(range(7), 0)
    for p in progress_list:
        level_counts[p.current_level] += 1

    completion = (learned_words / total_words * 100) if total_words > 0 else 0

    return {
        "cycle": current_cycle,
        "total_words": total_words,
        "learned_words": learned_words,
        "mastered_words": mastered_words,
        "completion_percentage": round(completion, 2),
        "current_level_counts": level_counts,
        "level_names": {i: get_level_name(i) for i in range(1, 7)},
    }


@router.post("/reset-progress", response_model=APIResponse)
def reset_progress(
    user_id: int = 1,  # TODO: Replace with auth
    session: Session = Depends(get_session),
):
    """
    Reset all learning progress for the current cycle.

    Args:
        user_id: User ID
        session: Database session

    Returns:
        API response with deleted count
    """
    # Get current cycle
    cycle_stmt = select(LearningProgress).where(
        LearningProgress.user_id == user_id,
    )
    all_progress = session.exec(cycle_stmt).all()

    current_cycle = 1 if not all_progress else max(p.cycle for p in all_progress)

    # Delete all progress records for current cycle
    delete_stmt = select(LearningProgress).where(
        LearningProgress.user_id == user_id,
        LearningProgress.cycle == current_cycle,
    )
    records_to_delete = session.exec(delete_stmt).all()
    deleted_count = len(records_to_delete)

    for record in records_to_delete:
        session.delete(record)

    session.commit()

    return APIResponse(
        success=True,
        message=f"已重置学习进度, 删除了 {deleted_count} 条记录",
        data={"deleted_count": deleted_count},
    )
