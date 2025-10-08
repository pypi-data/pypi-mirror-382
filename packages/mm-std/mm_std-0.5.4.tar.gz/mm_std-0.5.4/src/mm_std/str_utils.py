from collections.abc import Iterable


def str_starts_with_any(value: str, prefixes: Iterable[str]) -> bool:
    """Check if string starts with any of the given prefixes."""
    return any(value.startswith(prefix) for prefix in prefixes)


def str_ends_with_any(value: str, suffixes: Iterable[str]) -> bool:
    """Check if string ends with any of the given suffixes."""
    return any(value.endswith(suffix) for suffix in suffixes)


def str_contains_any(value: str, substrings: Iterable[str]) -> bool:
    """Check if string contains any of the given substrings."""
    return any(substring in value for substring in substrings)


def parse_lines(
    text: str,
    lowercase: bool = False,
    remove_comments: bool = False,
    deduplicate: bool = False,
) -> list[str]:
    """Parse multiline text into a list of cleaned lines.

    Args:
        text: Input text to parse
        lowercase: Convert all lines to lowercase
        remove_comments: Remove everything after '#' character in each line
        deduplicate: Remove duplicate lines while preserving order

    Returns:
        List of non-empty, stripped lines after applying specified transformations
    """
    if lowercase:
        text = text.lower()
    result = [line.strip() for line in text.split("\n") if line.strip()]
    if remove_comments:
        result = [line.split("#")[0].strip() for line in result]
        result = [line for line in result if line]
    if deduplicate:
        result = list(dict.fromkeys(result))

    return result
