"""Pydantic schemas for API requests and responses."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# Word schemas
class MeaningItem(BaseModel):
    """A single meaning of a word."""

    meaning: str = Field(..., description="义项解释")
    examples: list[str] = Field(default_factory=list, description="例句")


class WordData(BaseModel):
    """Word data for the quiz."""

    word: str = Field(..., description="文言文词语")
    type: str = Field(..., description="词语类型：实词/虚词")
    meanings: list[MeaningItem] = Field(..., description="所有义项")
    level: str = Field(default="common", description="常见程度")


class QuizQuestion(BaseModel):
    """A quiz question."""

    word: str
    question_type: str  # "meaning_to_word" or "word_to_meaning"
    options: list[str]
    correct_answer: str
    context_example: str | None = None


class QuizAnswer(BaseModel):
    """User's answer to a quiz question."""

    question_id: str
    user_answer: str
    is_correct: bool
    time_spent_seconds: int | None = None


class QuizSession(BaseModel):
    """A quiz session with multiple questions."""

    session_id: str
    questions: list[QuizQuestion]
    total_count: int


class AnswerSubmission(BaseModel):
    """Submit answers for a quiz session."""

    session_id: str
    answers: list[QuizAnswer]


# Review schemas
class ReviewItem(BaseModel):
    """An item for review."""

    word: str
    weak_meanings: list[MeaningItem]
    error_count: int
    last_error_at: datetime
    next_review_at: datetime


class ReviewList(BaseModel):
    """List of items due for review."""

    items: list[ReviewItem]
    total_count: int
    due_now: int


# Response wrappers
class APIResponse(BaseModel):
    """Standard API response wrapper."""

    success: bool
    message: str | None = None
    data: dict | None = None
