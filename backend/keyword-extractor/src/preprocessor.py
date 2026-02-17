"""
Preprocessor Module
Handles text normalization and cleaning.
"""

import re
import unicodedata


def normalize_unicode(text: str) -> str:
    """Normalize unicode characters to their closest ASCII equivalent where sensible."""
    # Normalize to NFKC form (compatibility decomposition, then canonical composition)
    return unicodedata.normalize("NFKC", text)


def remove_urls(text: str) -> str:
    """Remove URLs from text."""
    # Match http(s) URLs
    url_pattern = r"https?://[^\s]+"
    return re.sub(url_pattern, " ", text)


def remove_emails(text: str) -> str:
    """Remove email addresses from text."""
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    return re.sub(email_pattern, " ", text)


def remove_salary_ranges(text: str) -> str:
    """Remove salary/compensation figures."""
    # Match patterns like $84,200, USD$150,000, $130,000—$300,000
    salary_pattern = r"\$[\d,]+(?:\s*[-—–]\s*\$?[\d,]+)?"
    text = re.sub(salary_pattern, " ", text)

    # Match USD amounts
    usd_pattern = r"USD\s*\$?[\d,]+(?:\s*[-—–]\s*(?:USD\s*)?\$?[\d,]+)?"
    return re.sub(usd_pattern, " ", text)


def normalize_whitespace(text: str) -> str:
    """Collapse multiple whitespace characters into single spaces."""
    # Replace newlines and tabs with spaces
    text = re.sub(r"[\n\r\t]+", " ", text)
    # Collapse multiple spaces
    text = re.sub(r" +", " ", text)
    return text.strip()


def preprocess_text(text: str) -> str:
    """
    Apply all preprocessing steps to text.

    Note: We preserve case and special characters needed for tech terms
    (C++, .NET, Node.js, etc.)

    Args:
        text: Raw text from job description

    Returns:
        Cleaned text
    """
    text = normalize_unicode(text)
    text = remove_urls(text)
    text = remove_emails(text)
    text = remove_salary_ranges(text)
    text = normalize_whitespace(text)
    return text


def get_lowercase_for_matching(text: str) -> str:
    """
    Get lowercase version of text for case-insensitive matching.
    Original text should be preserved for output.
    """
    return text.lower()
