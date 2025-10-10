from pathlib import Path
from better_profanity import profanity

# Default bad words list bundled in package
DEFAULT_BAD_WORDS = Path(__file__).parent / "block_words"


class ProfanityError(ValueError):
    pass


def load_hinglish_profanity(file_path: Path = DEFAULT_BAD_WORDS):
    """
    Load Hinglish bad words from a file.
    Each line in the file should contain one word.
    """
    if not file_path.exists():
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]


def contains_hinglish_profanity(text: str, bad_words=None) -> bool:
    """
    Check if the given text contains Hinglish or English profanity.
    Returns True if bad words are found, else False.
    """
    if bad_words is None:
        bad_words = load_hinglish_profanity()

    profanity.load_censor_words()

    text_lower = text.lower()

    return profanity.contains_profanity(text_lower) or any(
        word in text_lower for word in bad_words
    )
