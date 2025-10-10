"""Word classes for character attributes and nouns."""

from typing import Any


class NominativAdjective:
    """Represents a nominative adjective with multilingual support."""

    def __init__(self, word_id: int, words: dict[str, dict[str, str]]) -> None:
        """
        Constructor for the NominativAdjective class.

        :param word_id: ID of the adjective
        :param words: A dictionary that contains the words in different languages and genders
        """
        self.word_id = word_id
        self.validate_words(words)
        self.words = words

    def __str__(self) -> str:
        return str(
            self.words.get("en", {}).get("neutral", "No neutral English word available")
        )

    def __repr__(self) -> str:
        return f"Adjective: {self.word_id} - {self.words}"

    @staticmethod
    def validate_words(words: dict[str, dict[str, str]]) -> None:
        """
        Validates the structure of the words dictionary. The dictionary should contain languages as keys
        and dictionaries as values, with the inner dictionaries having genders as keys and words as values.

        :param words: Dictionary to validate
        :raises ValueError: If the dictionary structure is invalid
        """
        for language, genders in words.items():
            if not isinstance(genders, dict):
                raise ValueError(
                    f"The value for language '{language}' must be a dictionary."
                )
            for gender in genders:
                if gender not in ["masculine", "feminine", "neutral"]:
                    raise ValueError(
                        f"Invalid gender '{gender}' for language '{language}'."
                    )

    def word(self, language: str, gender: str = "neutral") -> str:
        """
        Returns the word in the specified language and gender.

        :param language: The language of the word
        :param gender: The gender of the word. Options are "masculine", "feminine", and "neutral".
                       If no gender is specified, the neutral word is returned.
        :return: The word in the specified language and gender
        """
        try:
            return str(self.words[language][gender])
        except KeyError as exc:
            raise ValueError(
                f"No word found for the language '{language}' and gender '{gender}'."
            ) from exc

    def set_word(self, language: str, gender: str, word: str) -> None:
        """Set a word for a specific language and gender."""
        self.words[language][gender] = word

    def as_json(self) -> dict[str, Any]:
        """
        Returns a JSON-compatible dictionary that contains the attributes of the adjective.

        :return: A dictionary that contains the attributes of the adjective
        """
        return {"id": self.word_id, "words": self.words}


class CharacterNoun:
    """Represents a character noun with multilingual word and gender information."""

    def __init__(self, character_id: int, data: dict[str, dict[str, str]]) -> None:
        """
        Constructor for the CharacterNoun class.

        :param character_id: ID of the noun
        :param data: A dictionary containing the word and gender information in different languages
        """
        self.character_id = character_id
        self.data = data

    def __str__(self) -> str:
        return self.get_attribute("en", "word")

    def __repr__(self) -> str:
        return f"CharacterNoun: {self.character_id} - {self.data}"

    def get_attribute(self, language: str, attribute: str) -> str:
        """
        Returns the specified attribute in the specified language.

        :param language: The language of the attribute
        :param attribute: The attribute to get. Options are 'word' and 'gender'.
        :return: The attribute in the specified language
        """
        try:
            return str(self.data[language][attribute])
        except KeyError as exc:
            raise ValueError(
                f"No {attribute} found for the language '{language}'."
            ) from exc

    def as_json(self) -> dict[str, Any]:
        """
        Returns a JSON-compatible dictionary that contains the attributes of the noun.

        :return: A dictionary that contains the attributes of the noun
        """
        return {"character_id": self.character_id, "data": self.data}

    @staticmethod
    def from_json(json: dict[str, Any]) -> "CharacterNoun":
        """
        Returns a CharacterNoun object from a JSON-compatible dictionary.

        :param json: A JSON-compatible dictionary that contains the attributes of the noun
        :return: A CharacterNoun object
        """
        return CharacterNoun(json["character_id"], json["data"])
