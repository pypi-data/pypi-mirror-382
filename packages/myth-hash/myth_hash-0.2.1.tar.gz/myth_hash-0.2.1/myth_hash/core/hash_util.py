"""Hash utility functions for generating character names."""

import hashlib

from .character_data_loader import CharacterData, CharacterDataLoader

SUPPORTED_LANGUAGES = {"en", "de"}


def check_language(language: str) -> None:
    """Check if the given language is supported."""
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language '{language}'. Supported languages are: {', '.join(SUPPORTED_LANGUAGES)}."
        )


def generate_indices(input_string: str, list_sizes: list[int]) -> list[int]:
    """Generate indices from input string hash for selecting character attributes."""
    sha256 = hashlib.sha256(input_string.encode())
    d = sha256.digest()
    hash_length = len(d)
    indices = []

    for i, size in enumerate(list_sizes):
        start = (hash_length // len(list_sizes)) * i
        end = start + (hash_length // len(list_sizes))

        segment = int.from_bytes(d[start:end], "big")

        index = segment % size
        indices.append(index)

    return indices


def hash_name(input_string: str, language: str = "en") -> tuple[str, str, str]:
    """Generate a fantasy character name from an input string.

    Args:
        input_string: The string to hash
        language: The language for the output (default: "en")

    Returns:
        A tuple of (physical_attribute, personality_attribute, character_noun)
    """
    check_language(language)

    data_loader = CharacterDataLoader()
    character_data: CharacterData = data_loader.character_data

    indices = generate_indices(
        input_string,
        [
            len(character_data.physical_attributes),
            len(character_data.personality_attributes),
            len(character_data.character_nouns),
        ],
    )

    physical_attr_index = indices[0]
    personality_attr_index = indices[1]
    character_nouns_index = indices[2]

    character_noun = character_data.character_nouns[character_nouns_index]
    physical_attr = character_data.physical_attributes[physical_attr_index].word(
        language, character_noun.get_attribute(language, "gender")
    )
    personality_attr = character_data.personality_attributes[
        personality_attr_index
    ].word(language, character_noun.get_attribute(language, "gender"))
    return (
        physical_attr,
        personality_attr,
        character_noun.get_attribute(language, "word"),
    )
