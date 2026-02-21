"""Unit tests for quiz generation logic."""

import pytest
from wenyanwen.services.word_loader import word_loader
from wenyanwen.api.v1.quiz import (
    generate_multiple_choice,
    generate_true_false,
    generate_card,
    generate_flashcard,
)


class TestGenerateCard:
    """Test card question generation."""

    def test_card_has_front_and_back(self):
        """Test that card has front and back with correct structure."""
        # Get a word from the loader
        words = word_loader.get_all_words()
        if not words:
            pytest.skip("No words available")
        word_data = words[0]

        card = generate_card(word_data)

        assert card.word_id == word_data.id
        assert card.word == word_data.word
        assert card.question_type == "card"
        assert "sentence" in card.front
        assert "source" in card.front
        assert "meanings" in card.back
        assert len(card.back["meanings"]) == len(word_data.meanings)

    def test_card_displays_pinyin(self):
        """Test that card includes pinyin when available."""
        words = word_loader.get_all_words()
        if not words:
            pytest.skip("No words available")

        # Find a word with pinyin
        word_with_pinyin = None
        for w in words:
            if w.pinyin:
                word_with_pinyin = w
                break

        if not word_with_pinyin:
            pytest.skip("No word with pinyin found")

        card = generate_card(word_with_pinyin)
        assert card.pinyin == word_with_pinyin.pinyin

    def test_card_includes_mnemonics(self):
        """Test that card includes mnemonics when available."""
        words = word_loader.get_all_words()
        if not words:
            pytest.skip("No words available")

        # Find a word with mnemonics
        word_with_mnemonics = None
        for w in words:
            if w.mnemonics:
                word_with_mnemonics = w
                break

        if not word_with_mnemonics:
            pytest.skip("No word with mnemonics found")

        card = generate_card(word_with_mnemonics)
        assert card.back["mnemonics"] == word_with_mnemonics.mnemonics


class TestGenerateMultipleChoice:
    """Test multiple choice question generation."""

    def test_multiple_choice_has_four_options(self):
        """Test that multiple choice has exactly 4 options."""
        words = word_loader.get_all_words()
        if not words:
            pytest.skip("No words available")
        word_data = words[0]

        question = generate_multiple_choice(word_data)

        assert len(question.options) == 4
        assert question.correct_answer in question.options

    def test_multiple_choice_options_are_unique(self):
        """Test that multiple choice options are unique."""
        words = word_loader.get_all_words()
        if not words:
            pytest.skip("No words available")
        word_data = words[0]

        question = generate_multiple_choice(word_data)

        assert len(question.options) == len(set(question.options))

    def test_multiple_choice_has_correct_structure(self):
        """Test that multiple choice has correct structure."""
        words = word_loader.get_all_words()
        if not words:
            pytest.skip("No words available")
        word_data = words[0]

        question = generate_multiple_choice(word_data)

        assert question.word_id == word_data.id
        assert question.word == word_data.word
        assert question.question_type == "multiple_choice"
        assert question.example_sentence
        assert question.example_source
        assert question.correct_meaning_id


class TestGenerateTrueFalse:
    """Test true/false question generation."""

    def test_true_false_has_valid_structure(self):
        """Test that true/false has valid structure."""
        words = word_loader.get_all_words()
        if not words:
            pytest.skip("No words available")
        word_data = words[0]

        question = generate_true_false(word_data)

        assert question.word_id == word_data.id
        assert question.word == word_data.word
        assert question.question_type == "true_false"
        assert question.example_sentence
        assert question.example_source
        assert question.given_meaning
        assert isinstance(question.is_correct, bool)

    def test_true_false_can_be_true(self):
        """Test that true/false can be correct."""
        # Generate multiple times and check if any are true
        words = word_loader.get_all_words()
        if not words:
            pytest.skip("No words available")
        word_data = words[0]

        # Try multiple times since it's random
        found_true = False
        for _ in range(20):
            question = generate_true_false(word_data)
            if question.is_correct:
                found_true = True
                break

        assert found_true, "Should generate at least one true statement in 20 tries"

    def test_true_false_can_be_false(self):
        """Test that true/false can be incorrect."""
        words = word_loader.get_all_words()
        if not words:
            pytest.skip("No words available")
        word_data = words[0]

        # Try multiple times since it's random
        found_false = False
        for _ in range(20):
            question = generate_true_false(word_data)
            if not question.is_correct:
                found_false = True
                break

        assert found_false, "Should generate at least one false statement in 20 tries"


class TestGenerateFlashcard:
    """Test flashcard question generation."""

    def test_flashcard_has_valid_structure(self):
        """Test that flashcard has valid structure."""
        words = word_loader.get_all_words()
        if not words:
            pytest.skip("No words available")
        word_data = words[0]

        question = generate_flashcard(word_data)

        assert question.word_id == word_data.id
        assert question.word == word_data.word
        assert question.question_type == "flashcard"
        assert question.example_sentence
        assert question.example_source
        assert question.correct_meaning
