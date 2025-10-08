"""Core text utility functions."""


def clean_text(text: str) -> str:
    """
    Cleans text by stripping whitespace, normalizing spaces, and lowercasing.

    Args:
        text: Input string to clean.

    Returns:
        Cleaned string.

    Example:
        >>> clean_text("  Hello World!  ")
        'hello world!'
    """

    return " ".join(text.strip().lower().split())


def word_count(text: str) -> int:
    """
    Counts words in the text.

    Args:
        text: Input string.

    Returns:
        Number of words.

    Example:
        >>> word_count("Hello World!")
        2
    """

    return len(clean_text(text).split())


def slugify(text: str) -> str:
    """
    Converts text to a URL-friendly slug.

    Args:
        text: Input string.

    Returns:
        Slugified string.

    Example:
        >>> slugify("Hello World!")
        'hello-world'
    """

    cleaned = clean_text(text)
    slug = "-".join(word.strip("!@#$%^&*()") for word in cleaned.split())
    return slug.strip("-")
