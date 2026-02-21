"""Word data loader from JSON file."""

import json
import random
from pathlib import Path

from ..schemas import WordData, WordLibrary


class WordLoader:
    """Load and manage word data from JSON file."""

    def __init__(self, data_path: Path | None = None) -> None:
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
        self._library: WordLibrary | None = None

    def load(self) -> WordLibrary:
        """
        Load words from JSON file.

        Returns:
            WordLibrary containing all words
        """
        if self._library is not None:
            return self._library

        if not self.data_path.exists():
            self._library = WordLibrary(words=[], metadata={})
            return self._library

        with open(self.data_path, encoding="utf-8") as f:
            data = json.load(f)
            self._library = WordLibrary(**data)

        return self._library

    def reload(self) -> WordLibrary:
        """Force reload words from JSON file."""
        self._library = None
        return self.load()

    def get_word_by_id(self, word_id: str) -> WordData | None:
        """
        Get a word by its ID.

        Args:
            word_id: The word ID to look up

        Returns:
            WordData if found, None otherwise
        """
        library = self.load()
        for word in library.words:
            if word.id == word_id:
                return word
        return None

    def get_word_by_text(self, word_text: str) -> WordData | None:
        """
        Get a word by its text.

        Args:
            word_text: The word text to look up

        Returns:
            WordData if found, None otherwise
        """
        library = self.load()
        for word in library.words:
            if word.word == word_text:
                return word
        return None

    def get_all_words(self) -> list[WordData]:
        """Get all loaded words."""
        library = self.load()
        return library.words

    def get_words_by_type(self, word_type: str) -> list[WordData]:
        """
        Get words filtered by type.

        Args:
            word_type: Type of word (e.g., "实词", "虚词")

        Returns:
            List of words of the specified type
        """
        library = self.load()
        return [w for w in library.words if w.type == word_type]

    def get_new_words(
        self,
        exclude_ids: set[str],
        count: int = 10,
        mode: str = "sequential",
    ) -> list[WordData]:
        """
        Get new words that haven't been learned yet.

        Args:
            exclude_ids: Set of word IDs to exclude (already learned)
            count: Number of words to return
            mode: "sequential" or "random"

        Returns:
            List of new words to learn
        """
        library = self.load()
        available = [w for w in library.words if w.id not in exclude_ids]

        if mode == "random":
            available = random.sample(available, min(len(available), count))
        else:  # sequential
            available = available[:count]

        return available

    @property
    def total_count(self) -> int:
        """Get total number of words in library."""
        library = self.load()
        return len(library.words)


# Global word loader instance
word_loader = WordLoader()
