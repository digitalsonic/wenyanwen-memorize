"""SQLModel database models."""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    """Base user model."""

    username: str = Field(index=True, unique=True)


class User(UserBase, table=True):
    """User database model."""

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)


class UserCreate(UserBase):
    """Model for creating a user."""


class UserPublic(UserBase):
    """Public user model (without sensitive data)."""

    id: int


class QuizRecordBase(SQLModel):
    """Base quiz record model."""

    word: str = Field(index=True)
    meaning: str
    is_correct: bool


class QuizRecord(QuizRecordBase, table=True):
    """Quiz record database model."""

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    next_review_at: datetime | None = None
    review_count: int = Field(default=0)


class QuizRecordCreate(QuizRecordBase):
    """Model for creating a quiz record."""

    user_id: int


class QuizRecordPublic(QuizRecordBase):
    """Public quiz record model."""

    id: int
    user_id: int
    next_review_at: datetime | None
    review_count: int


class WeakMeaning(SQLModel, table=True):
    """Weak meaning tracking for spaced repetition."""

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    word: str = Field(index=True)
    meaning: str
    error_count: int = Field(default=1)
    last_error_at: datetime = Field(default_factory=datetime.now)
    next_review_at: datetime
