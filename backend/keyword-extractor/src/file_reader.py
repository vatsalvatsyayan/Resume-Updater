"""
File Reader Module
Handles reading job description files from the input directory.
"""

import re
from pathlib import Path
from typing import Generator
from dataclasses import dataclass


@dataclass
class JobDescription:
    """Represents a single job description with metadata."""
    company: str
    filename: str
    content: str


def extract_company_name(filename: str) -> str:
    """
    Extract company name from filename pattern: {Company}_job_description.txt
    Handles underscores and special characters in company names.
    """
    # Remove _job_description.txt suffix
    pattern = r"(.+?)_job_description\.txt$"
    match = re.match(pattern, filename, re.IGNORECASE)
    if match:
        # Replace underscores with spaces for readability
        return match.group(1).replace("_", " ")
    # Fallback: use filename without extension
    return Path(filename).stem


def read_job_descriptions(input_dir: str | Path) -> Generator[JobDescription, None, None]:
    """
    Read all .txt files from the input directory.

    Yields:
        JobDescription objects with company name, filename, and content.
    """
    input_path = Path(input_dir)

    if not input_path.exists():
        raise FileNotFoundError(f"Input directory not found: {input_path}")

    if not input_path.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {input_path}")

    txt_files = sorted(input_path.glob("*.txt"))

    if not txt_files:
        raise ValueError(f"No .txt files found in: {input_path}")

    for file_path in txt_files:
        try:
            # Try UTF-8 first, fall back to latin-1
            try:
                content = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                content = file_path.read_text(encoding="latin-1")

            company = extract_company_name(file_path.name)

            yield JobDescription(
                company=company,
                filename=file_path.name,
                content=content
            )
        except Exception as e:
            print(f"Warning: Failed to read {file_path.name}: {e}")
            continue


def get_all_job_descriptions(input_dir: str | Path) -> list[JobDescription]:
    """
    Read all job descriptions and return as a list.

    Returns:
        List of JobDescription objects.
    """
    return list(read_job_descriptions(input_dir))
