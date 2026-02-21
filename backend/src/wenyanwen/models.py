"""SQLModel database models."""

from datetime import datetime
from enum import Enum

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


class QuizType(str, Enum):
    """Quiz question types."""

    CARD = "card"  # 双面卡片（初学）
    FLASHCARD = "flashcard"  # 闪卡（主动回忆）
    MULTIPLE_CHOICE = "multiple_choice"  # 单选题
    TRUE_FALSE = "true_false"  # 判断题


class LearningProgress(SQLModel, table=True):
    """Learning progress tracking with cycle-based spaced repetition."""

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    word_id: str = Field(index=True, description="Word ID from words.json")
    cycle: int = Field(default=1, description="Current learning cycle (1, 2, 3...)")

    current_level: int = Field(default=0, description="0=new, 1-6=review levels")
    error_count: int = Field(default=0, description="Error count at current level")
    is_mastered: bool = Field(default=False, description="Whether word is mastered in this cycle")

    last_review_at: datetime | None = None
    next_review_at: datetime | None = Field(index=True)

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class LearningProgressCreate(SQLModel):
    """Model for creating learning progress."""

    user_id: int
    word_id: str
    cycle: int = 1


class LearningProgressPublic(SQLModel):
    """Public learning progress model."""

    id: int
    user_id: int
    word_id: str
    cycle: int
    current_level: int
    error_count: int
    is_mastered: bool
    last_review_at: datetime | None
    next_review_at: datetime | None


class QuizRecordBase(SQLModel):
    """Base quiz record model."""

    word: str = Field(index=True)
    meaning: str
    is_correct: bool


class QuizRecord(QuizRecordBase, table=True):
    """Quiz record database model (legacy, kept for compatibility)."""

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
    """Weak meaning tracking for spaced repetition (legacy, kept for compatibility)."""

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    word: str = Field(index=True)
    meaning: str
    error_count: int = Field(default=1)
    last_error_at: datetime = Field(default_factory=datetime.now)
    next_review_at: datetime
