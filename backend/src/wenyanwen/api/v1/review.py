"""Review API endpoints."""

from fastapi import APIRouter, Depends
from sqlmodel import Session
from datetime import datetime

from ...database import get_session
from ...schemas import ReviewList, APIResponse

router = APIRouter()


@router.get("/list", response_model=ReviewList)
def get_review_list(
    user_id: int = 1,  # TODO: Replace with auth
    session: Session = Depends(get_session),
):
    """
    Get list of items due for review.

    Args:
        user_id: User ID (TODO: Replace with auth)
        session: Database session

    Returns:
        List of review items
    """
    # TODO: Implement review list logic with Ebbinghaus scheduling
    return ReviewList(
        items=[],
        total_count=0,
        due_now=0,
    )


@router.post("/acknowledge", response_model=APIResponse)
def acknowledge_review(
    word: str,
    user_id: int = 1,
    session: Session = Depends(get_session),
):
    """
    Acknowledge a review item (mark as reviewed).

    Args:
        word: The word being reviewed
        user_id: User ID (TODO: Replace with auth)
        session: Database session

    Returns:
        API response
    """
    # TODO: Implement acknowledgment logic
    return APIResponse(
        success=True,
        message=f"已确认复习: {word}",
    )
