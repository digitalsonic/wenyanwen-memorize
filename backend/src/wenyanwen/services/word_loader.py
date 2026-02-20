"""Word data loader from JSON file."""

import json
from pathlib import Path
from typing import Optional

from ..schemas import WordData


class WordLoader:
    """Load and manage word data from JSON file."""

    def __init__(self, data_path: Optional[Path] = None) -> None:
        """
        Initialize the word loader.

        Args:
            data_path: Path to the words JSON file
        """
        if data_path is None:
            # Default to backend/data/words.json
            project_root = Path(__file__).parent.parent.parent.parent
            data_path = project_root / "data" / "words.json"
        self.data_path = Path(data_path)
        self._words: dict[str, WordData] = {}

    def load(self) -> None:
        """Load words from JSON file."""
        if not self.data_path.exists():
            self._words = {}
            return

        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for word_data in data.get("words", []):
                word = WordData(**word_data)
                self._words[word.word] = word

    def get_word(self, word: str) -> Optional[WordData]:
        """
        Get a word by its text.

        Args:
            word: The word to look up

        Returns:
            WordData if found, None otherwise
        """
        if not self._words:
            self.load()
        return self._words.get(word)

    def get_all_words(self) -> list[WordData]:
        """Get all loaded words."""
        if not self._words:
            self.load()
        return list(self._words.values())

    def get_words_by_type(self, word_type: str) -> list[WordData]:
        """
        Get words filtered by type.

        Args:
            word_type: Type of word (e.g., "实词", "虚词")

        Returns:
            List of words of the specified type
        """
        if not self._words:
            self.load()
        return [w for w in self._words.values() if w.type == word_type]


# Global word loader instance
word_loader = WordLoader()
