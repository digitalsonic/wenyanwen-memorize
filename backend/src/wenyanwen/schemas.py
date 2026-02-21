"""Pydantic schemas for API requests and responses."""

from datetime import datetime

from pydantic import BaseModel, Field

# Import enums from models
from wenyanwen.models import QuizType


# Word schemas
class ExampleItem(BaseModel):
    """An example sentence with source."""

    sentence: str = Field(..., description="例句")
    source: str = Field(..., description="出处")


class MeaningItem(BaseModel):
    """A single meaning of a word."""

    id: str = Field(..., description="义项ID")
    definition: str = Field(..., description="义项解释")
    examples: list[ExampleItem] = Field(default_factory=list, description="例句列表")


class WordData(BaseModel):
    """Word data for the quiz."""

    id: str = Field(..., description="词语ID")
    word: str = Field(..., description="文言文词语")
    type: str = Field(..., description="词语类型：实词/虚词")
    pinyin: str | None = Field(None, description="拼音")
    meanings: list[MeaningItem] = Field(..., description="所有义项")
    mnemonics: str | None = Field(None, description="助记口诀")


class WordLibrary(BaseModel):
    """Complete word library."""

    words: list[WordData]
    metadata: dict | None = None


# Quiz schemas - Multiple choice
class MultipleChoiceQuestion(BaseModel):
    """Multiple choice quiz question."""

    word_id: str
    word: str
    question_type: QuizType = QuizType.MULTIPLE_CHOICE
    example_sentence: str
    example_source: str
    options: list[str]  # 4 options
    correct_answer: str  # The correct meaning definition
    correct_meaning_id: str


class TrueFalseQuestion(BaseModel):
    """True/false quiz question."""

    word_id: str
    word: str
    question_type: QuizType = QuizType.TRUE_FALSE
    example_sentence: str
    example_source: str
    given_meaning: str
    is_correct: bool  # Whether the given meaning is correct


class CardQuestion(BaseModel):
    """Card quiz question (front and back)."""

    word_id: str
    word: str
    question_type: QuizType = QuizType.CARD
    pinyin: str | None = None
    front: dict  # {sentence, source}
    back: dict  # {meanings: [...], mnemonics: ...}


class FlashcardQuestion(BaseModel):
    """Flashcard quiz question (active recall)."""

    word_id: str
    word: str
    question_type: QuizType = QuizType.FLASHCARD
    example_sentence: str
    example_source: str
    correct_meaning: str


# Union type for all question types
QuizQuestion = MultipleChoiceQuestion | TrueFalseQuestion | CardQuestion | FlashcardQuestion


class QuizSession(BaseModel):
    """A quiz session with multiple questions."""

    session_id: str
    level: int  # 0=new, 1-6=review levels
    questions: list[QuizQuestion]
    total_count: int


# Answer schemas
class QuizAnswer(BaseModel):
    """User's answer to a quiz question."""

    word_id: str
    question_type: QuizType
    user_answer: str | bool  # str for multiple_choice, bool for true_false
    is_correct: bool
    time_spent_seconds: int | None = None


class AnswerSubmission(BaseModel):
    """Submit answers for a quiz session."""

    level: int
    answers: list[QuizAnswer]


class RetryRequest(BaseModel):
    """Request to retry wrong answers."""

    wrong_answer_ids: list[str]


# Review schemas
class ReviewItem(BaseModel):
    """An item for review."""

    word_id: str
    word: str
    level: int
    quiz_type: QuizType
    error_count: int
    last_review_at: datetime | None
    next_review_at: datetime
    word_data: WordData


class ReviewList(BaseModel):
    """List of items due for review, grouped by level."""

    items: list[ReviewItem]
    total_count: int
    grouped: dict[int, list[ReviewItem]]  # level -> items


# Learn new words schemas
class LearnRequest(BaseModel):
    """Request to learn new words."""

    count: int = Field(default=10, description="Number of new words to learn")
    mode: str = Field(default="sequential", description="sequential or random")


class LearnSession(BaseModel):
    """New words learning session."""

    session_id: str
    words: list[CardQuestion]
    total_count: int
    remaining_count: int


# Progress schemas
class LearningProgressSummary(BaseModel):
    """Summary of learning progress."""

    cycle: int
    total_words: int
    learned_words: int  # Words with level > 0
    mastered_words: int  # Words with is_mastered = True
    completion_percentage: float
    current_level_counts: dict[int, int]  # level -> count


# Response wrappers
class APIResponse(BaseModel):
    """Standard API response wrapper."""

    success: bool
    message: str | None = None
    data: dict | None = None
