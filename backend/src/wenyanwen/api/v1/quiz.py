"""Quiz API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ...database import get_session
from ...schemas import (
    QuizQuestion,
    QuizSession,
    AnswerSubmission,
    APIResponse,
)

router = APIRouter()


@router.get("/start", response_model=QuizSession)
def start_quiz(
    count: int = 10,
    user_id: int = 1,  # TODO: Replace with auth
    session: Session = Depends(get_session),
):
    """
    Start a new quiz session.

    Args:
        count: Number of questions to generate
        user_id: User ID (TODO: Replace with auth)
        session: Database session

    Returns:
        A quiz session with questions
    """
    # TODO: Implement quiz generation logic
    return QuizSession(
        session_id="placeholder",
        questions=[],
        total_count=0,
    )


@router.post("/submit", response_model=APIResponse)
def submit_answer(
    submission: AnswerSubmission,
    session: Session = Depends(get_session),
):
    """
    Submit answers for a quiz session.

    Args:
        submission: Answer submission data
        session: Database session

    Returns:
        API response with results
    """
    # TODO: Implement answer submission logic
    return APIResponse(
        success=True,
        message="答案已提交",
        data={"correct_count": 0, "total_count": 0},
    )
