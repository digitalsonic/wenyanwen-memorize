"""Quiz API endpoints."""

import random
import uuid
from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ...database import get_session
from ...models import LearningProgress, QuizType
from ...schemas import (
    AnswerSubmission,
    APIResponse,
    CardQuestion,
    FlashcardQuestion,
    LearnRequest,
    LearnSession,
    MultipleChoiceQuestion,
    QuizSession,
    TrueFalseQuestion,
)
from ...services.spaced_repetition import (
    calculate_next_review,
    get_quiz_type,
)
from ...services.word_loader import word_loader

router = APIRouter()


def generate_multiple_choice(word_data) -> MultipleChoiceQuestion:
    """Generate a multiple choice question."""
    # Pick a random meaning as the correct answer
    correct_meaning = random.choice(word_data.meanings)
    correct_example = random.choice(correct_meaning.examples)

    # Generate distractors from other meanings of the same word
    # and from other words
    all_words = word_loader.get_all_words()
    other_meanings = []

    # Add other meanings from the same word
    for m in word_data.meanings:
        if m.id != correct_meaning.id:
            other_meanings.append(m.definition)

    # Add meanings from other words
    for w in all_words:
        if w.id != word_data.id:
            for m in w.meanings:
                other_meanings.append(m.definition)

    # Select 3 distractors
    distractors = random.sample(
        [m for m in other_meanings if m != correct_meaning.definition],
        min(3, len(other_meanings))
    )

    # Create options (correct answer + distractors)
    options = [correct_meaning.definition, *distractors]
    random.shuffle(options)

    return MultipleChoiceQuestion(
        word_id=word_data.id,
        word=word_data.word,
        question_type=QuizType.MULTIPLE_CHOICE,
        example_sentence=correct_example.sentence,
        example_source=correct_example.source,
        options=options,
        correct_answer=correct_meaning.definition,
        correct_meaning_id=correct_meaning.id,
    )


def generate_true_false(word_data) -> TrueFalseQuestion:
    """Generate a true/false question."""
    # Pick a random meaning
    selected_meaning = random.choice(word_data.meanings)
    selected_example = random.choice(selected_meaning.examples)

    # 50% chance to make it true or false
    if random.random() < 0.5:
        # True: given meaning matches
        given_meaning = selected_meaning.definition
        is_correct = True
    else:
        # False: given meaning is from a different meaning of the same word
        other_meanings = [m for m in word_data.meanings if m.id != selected_meaning.id]
        if other_meanings:
            given_meaning = random.choice(other_meanings).definition
        else:
            # Fallback: use a wrong meaning from another word
            all_words = word_loader.get_all_words()
            other_word = random.choice([w for w in all_words if w.id != word_data.id])
            given_meaning = random.choice(other_word.meanings).definition
        is_correct = False

    return TrueFalseQuestion(
        word_id=word_data.id,
        word=word_data.word,
        question_type=QuizType.TRUE_FALSE,
        example_sentence=selected_example.sentence,
        example_source=selected_example.source,
        given_meaning=given_meaning,
        is_correct=is_correct,
        correct_meaning=selected_meaning.definition,  # The actual correct meaning
    )


def generate_card(word_data) -> CardQuestion:
    """Generate a card question for learning new words."""
    # Pick a representative example for the front
    # Use the first meaning's example
    first_meaning = word_data.meanings[0]
    front_example = random.choice(first_meaning.examples)

    # Format meanings for back (no numbering - frontend will handle display)
    meanings_list = [m.definition for m in word_data.meanings]

    return CardQuestion(
        word_id=word_data.id,
        word=word_data.word,
        question_type=QuizType.CARD,
        pinyin=word_data.pinyin,
        front={
            "sentence": front_example.sentence,
            "source": front_example.source,
        },
        back={
            "meanings": meanings_list,
            "mnemonics": word_data.mnemonics,
        },
    )


def generate_flashcard(word_data) -> FlashcardQuestion:
    """Generate a flashcard question for active recall."""
    # Pick a random meaning
    selected_meaning = random.choice(word_data.meanings)
    selected_example = random.choice(selected_meaning.examples)

    return FlashcardQuestion(
        word_id=word_data.id,
        word=word_data.word,
        question_type=QuizType.FLASHCARD,
        example_sentence=selected_example.sentence,
        example_source=selected_example.source,
        correct_meaning=selected_meaning.definition,
        meaning_id=selected_meaning.id,
        mnemonics=word_data.mnemonics,
    )


@router.post("/learn", response_model=LearnSession)
def learn_new_words(
    request: LearnRequest,
    user_id: int = 1,  # TODO: Replace with auth
    session: Session = Depends(get_session),
):
    """
    Learn new words with card mode.

    Args:
        request: Learn request with count and mode
        user_id: User ID
        session: Database session

    Returns:
        A learning session with card questions
    """
    # Get already learned word IDs for current cycle
    progress_stmt = select(LearningProgress).where(
        LearningProgress.user_id == user_id,
        LearningProgress.current_level > 0,
    )
    progress_result = session.exec(progress_stmt)
    learned_ids = {p.word_id for p in progress_result}

    # Get new words
    new_words = word_loader.get_new_words(
        exclude_ids=learned_ids,
        count=request.count,
        mode=request.mode,
    )

    # Generate card questions
    cards = [generate_card(word) for word in new_words]

    return LearnSession(
        session_id=str(uuid.uuid4()),
        words=cards,
        total_count=len(cards),
        remaining_count=word_loader.total_count - len(learned_ids),
    )


@router.get("/review", response_model=QuizSession)
def start_review(
    level: int | None = None,
    user_id: int = 1,  # TODO: Replace with auth
    session: Session = Depends(get_session),
):
    """
    Start a review session for due words.

    Args:
        level: Filter by specific level (optional)
        user_id: User ID
        session: Database session

    Returns:
        A quiz session with questions
    """

    # Query due words for review
    stmt = select(LearningProgress).where(
        LearningProgress.user_id == user_id,
        LearningProgress.current_level > 0,
        LearningProgress.is_mastered == False,
    )

    progress_list = session.exec(stmt).all()

    # Filter by level if specified
    if level is not None:
        progress_list = [p for p in progress_list if p.current_level == level]

    # Filter by due date (consistent with review/list endpoint)
    today = date.today()
    due_progress = [
        p for p in progress_list
        if p.next_review_at is None or p.next_review_at.date() <= today
    ]

    # Generate questions based on level
    questions = []
    for progress in due_progress[:50]:  # Limit to 50 questions per session
        word_data = word_loader.get_word_by_id(progress.word_id)
        if not word_data:
            continue

        quiz_type = get_quiz_type(progress.current_level)

        if quiz_type == "multiple_choice":
            q = generate_multiple_choice(word_data)
            questions.append(q)
        elif quiz_type == "true_false":
            q = generate_true_false(word_data)
            questions.append(q)
        elif quiz_type == "flashcard":
            q = generate_flashcard(word_data)
            questions.append(q)

    return QuizSession(
        session_id=str(uuid.uuid4()),
        level=level or 0,
        questions=questions,
        total_count=len(questions),
    )


@router.post("/submit", response_model=APIResponse)
def submit_answers(
    submission: AnswerSubmission,
    user_id: int = 1,  # TODO: Replace with auth
    session: Session = Depends(get_session),
):
    """
    Submit answers for a quiz session.

    Args:
        submission: Answer submission data
        user_id: User ID
        session: Database session

    Returns:
        API response with results and wrong answers for retry
    """
    wrong_answer_ids = []

    for answer in submission.answers:
        # Get the learning progress record
        stmt = select(LearningProgress).where(
            LearningProgress.user_id == user_id,
            LearningProgress.word_id == answer.word_id,
        )
        progress = session.exec(stmt).first()

        if not progress:
            continue

        if answer.is_correct:
            # Correct answer: calculate next review
            next_review, new_level, is_mastered = calculate_next_review(
                current_level=progress.current_level,
                is_correct=True,
            )

            progress.current_level = new_level
            progress.is_mastered = is_mastered
            progress.next_review_at = next_review
            progress.last_review_at = datetime.now()
            progress.error_count = 0  # Reset error count on correct
        else:
            # Wrong answer: stay at same level, increment error count
            progress.error_count += 1
            progress.last_review_at = datetime.now()
            wrong_answer_ids.append(answer.word_id)

        progress.updated_at = datetime.now()
        session.add(progress)

    session.commit()

    # Return response with wrong answer info for retry
    return APIResponse(
        success=True,
        message="答案已提交",
        data={
            "correct_count": len(submission.answers) - len(wrong_answer_ids),
            "total_count": len(submission.answers),
            "wrong_answer_ids": wrong_answer_ids,
            "has_wrong": len(wrong_answer_ids) > 0,
        },
    )


@router.post("/learn/complete", response_model=APIResponse)
def complete_learning(
    word_ids: list[str],
    user_id: int = 1,  # TODO: Replace with auth
    session: Session = Depends(get_session),
):
    """
    Mark new words as learned (card mode completed).

    Args:
        word_ids: List of word IDs that were learned
        user_id: User ID
        session: Database session

    Returns:
        API response
    """
    for word_id in word_ids:
        # Check if progress already exists
        stmt = select(LearningProgress).where(
            LearningProgress.user_id == user_id,
            LearningProgress.word_id == word_id,
        )
        existing = session.exec(stmt).first()

        if existing:
            continue

        # Create new progress record
        next_review, _, _ = calculate_next_review(current_level=0, is_correct=True)

        progress = LearningProgress(
            user_id=user_id,
            word_id=word_id,
            cycle=1,
            current_level=1,  # Move to level 1 after learning
            error_count=0,
            is_mastered=False,
            next_review_at=next_review,
            last_review_at=datetime.now(),
        )
        session.add(progress)

    session.commit()

    return APIResponse(
        success=True,
        message=f"已标记 {len(word_ids)} 个词为已学习",
    )
