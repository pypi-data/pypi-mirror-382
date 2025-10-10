"""Data loader for character attributes and nouns."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .words import CharacterNoun, NominativAdjective

BASE_PATH = Path(__file__).parent.parent / "data"
CHARACTER_NOUNS_FILE = BASE_PATH / "character_nouns.json"
PHYSICAL_ATTRIBUTES_FILE = BASE_PATH / "physical_attributes.json"
PERSONALITY_ATTRIBUTES_FILE = BASE_PATH / "personality_attributes.json"


@dataclass
class CharacterData:
    """Container for character data including nouns and attributes."""

    character_nouns: list[CharacterNoun]
    physical_attributes: list[NominativAdjective]
    personality_attributes: list[NominativAdjective]


class CharacterDataLoader:
    """Singleton loader for character data from JSON files."""

    _instance: Optional["CharacterDataLoader"] = None
    _character_data: CharacterData | None = None

    def __new__(cls) -> "CharacterDataLoader":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_data()
        return cls._instance

    def _load_data(self) -> None:
        self._character_data = CharacterData(
            character_nouns=self._load_character_nouns(),
            physical_attributes=self._load_attributes(PHYSICAL_ATTRIBUTES_FILE),
            personality_attributes=self._load_attributes(PERSONALITY_ATTRIBUTES_FILE),
        )

    @staticmethod
    def _load_attributes(file_path: Path) -> list[NominativAdjective]:
        try:
            with open(file_path, encoding="utf8") as f:
                json_dict = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Error loading attributes from {file_path}: {e}") from e

        return [
            NominativAdjective(word_id, data["words"])
            for word_id, data in json_dict.items()
        ]

    @staticmethod
    def _load_character_nouns() -> list[CharacterNoun]:
        try:
            with open(CHARACTER_NOUNS_FILE, encoding="utf8") as f:
                json_dict = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise RuntimeError(
                f"Error loading character nouns from {CHARACTER_NOUNS_FILE}: {e}"
            ) from e

        return [
            CharacterNoun(char_id, data["data"]) for char_id, data in json_dict.items()
        ]

    @property
    def character_data(self) -> CharacterData:
        """Get the loaded character data."""
        if self._character_data is None:
            self._load_data()
        if self._character_data is None:
            raise RuntimeError("Character data not loaded")
        return self._character_data
