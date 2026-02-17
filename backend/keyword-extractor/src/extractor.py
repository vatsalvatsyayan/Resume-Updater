"""
Extractor Module
Handles candidate keyword extraction using multiple signals.
"""

import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Set

import spacy


@dataclass
class CandidateTerm:
    """Represents an extracted candidate term."""
    term: str
    original_forms: Set[str] = field(default_factory=set)
    sources: Set[str] = field(default_factory=set)
    count: int = 0
    signals: Set[str] = field(default_factory=set)  # Which extraction signals found it


class KeywordExtractor:
    """Extracts candidate tech keywords using multiple signals."""

    def __init__(self):
        # Load spaCy model with word vectors
        try:
            self.nlp = spacy.load("en_core_web_md")
        except OSError:
            print("Downloading spaCy model en_core_web_md...")
            spacy.cli.download("en_core_web_md")
            self.nlp = spacy.load("en_core_web_md")

        # Contextual phrases that often precede tech terms
        self.context_phrases = [
            r"experience with",
            r"experience in",
            r"proficiency in",
            r"proficient in",
            r"knowledge of",
            r"familiar with",
            r"familiarity with",
            r"expertise in",
            r"skilled in",
            r"working with",
            r"work with",
            r"using",
            r"including",
            r"such as",
            r"technologies like",
            r"tools like",
            r"languages like",
        ]
        self.context_pattern = re.compile(
            r"(?:" + "|".join(self.context_phrases) + r")\s+([^,.;:]+)",
            re.IGNORECASE
        )

    def extract_camelcase(self, text: str) -> Set[str]:
        """
        Extract CamelCase and PascalCase terms.
        Examples: PostgreSQL, JavaScript, GraphQL, TypeScript
        """
        # Match CamelCase: lowercase followed by uppercase, or sequences with mixed case
        pattern = r"\b([A-Z][a-z]+(?:[A-Z][a-z]*)+)\b"
        matches = re.findall(pattern, text)

        # Also match terms like iOS, gRPC (lowercase start, then uppercase)
        pattern2 = r"\b([a-z]+[A-Z][a-zA-Z]*)\b"
        matches.extend(re.findall(pattern2, text))

        return set(matches)

    def extract_allcaps(self, text: str) -> Set[str]:
        """
        Extract ALL_CAPS terms (often acronyms or config names).
        Examples: REST, API, CI_CD, AWS, GCP
        """
        # Match 2+ capital letters, optionally with underscores/numbers
        pattern = r"\b([A-Z][A-Z0-9_]{1,})\b"
        matches = re.findall(pattern, text)

        # Filter out common non-tech all-caps words
        common_words = {"THE", "AND", "FOR", "WITH", "THIS", "THAT", "FROM", "WILL",
                        "ARE", "WAS", "WERE", "BEEN", "HAVE", "HAS", "HAD", "NOT",
                        "BUT", "CAN", "ALL", "THEIR", "WHAT", "WHEN", "WHO", "HOW",
                        "USD", "USA", "INC"}
        return {m for m in matches if m not in common_words and len(m) >= 2}

    def extract_special_patterns(self, text: str) -> Set[str]:
        """
        Extract terms with special tech patterns.
        Examples: C++, C#, .NET, Node.js, Python3, OAuth2
        """
        results = set()

        # C++ and C#
        if re.search(r"\bC\+\+\b", text):
            results.add("C++")
        if re.search(r"\bC#\b", text):
            results.add("C#")

        # .NET variations
        dotnet = re.findall(r"\.NET(?:\s*(?:Core|Framework|Standard))?", text, re.IGNORECASE)
        results.update(dotnet)

        # Terms ending in .js (Node.js, React.js, Vue.js)
        js_terms = re.findall(r"\b([A-Za-z]+\.js)\b", text, re.IGNORECASE)
        results.update(js_terms)

        # Terms with numbers (Python3, H2O, S3, EC2, OAuth2)
        numbered = re.findall(r"\b([A-Za-z]+[0-9]+[A-Za-z]*)\b", text)
        results.update(numbered)

        # Also match number-first like 3D, K8s
        numbered2 = re.findall(r"\b([0-9]+[A-Za-z]+)\b", text)
        results.update(numbered2)

        # Hyphenated tech terms (CI-CD, back-end, full-stack)
        hyphenated = re.findall(r"\b([A-Za-z]+-[A-Za-z]+(?:-[A-Za-z]+)?)\b", text)
        results.update(hyphenated)

        return results

    def extract_noun_phrases(self, text: str) -> Set[str]:
        """
        Extract noun phrases using spaCy.
        Examples: distributed systems, machine learning, version control
        """
        doc = self.nlp(text)
        phrases = set()

        for chunk in doc.noun_chunks:
            # Get the text, normalize whitespace
            phrase = " ".join(chunk.text.split())

            # Only keep phrases 2-4 words (too short = likely noise, too long = sentence fragment)
            word_count = len(phrase.split())
            if 2 <= word_count <= 4:
                # Filter out phrases starting with common determiners/pronouns
                first_word = phrase.split()[0].lower()
                skip_words = {"the", "a", "an", "this", "that", "these", "those",
                              "my", "your", "our", "their", "its", "his", "her",
                              "some", "any", "all", "each", "every", "both"}
                if first_word not in skip_words:
                    phrases.add(phrase)

        return phrases

    def extract_from_context(self, text: str) -> Set[str]:
        """
        Extract terms that appear after contextual phrases.
        Examples: "experience with Python, Java, and Kubernetes"
        """
        results = set()
        matches = self.context_pattern.findall(text)

        for match in matches:
            # Split on common delimiters
            terms = re.split(r"[,;]|\band\b|\bor\b", match)
            for term in terms:
                term = term.strip()
                # Only keep reasonable length terms
                if 1 <= len(term.split()) <= 4 and len(term) >= 2:
                    results.add(term)

        return results

    def extract_single_tech_words(self, text: str) -> Set[str]:
        """
        Extract single words that look like tech terms.
        Focus on capitalized words that aren't at sentence start.
        """
        results = set()

        # Find capitalized words not at sentence start
        # Pattern: lowercase/punctuation followed by space, then capitalized word
        pattern = r"(?<=[a-z,.;:!?]\s)([A-Z][a-z]+)\b"
        matches = re.findall(pattern, text)
        results.update(matches)

        # Also extract specific known single-letter/short languages that need special handling
        # These are checked with word boundaries
        special_singles = {
            "Go": r"\bGo\b(?:\s+(?:language|programming|code))?",
            "R": r"\bR\b(?:\s+(?:language|programming|statistical))?",
            "C": r"\bC\b(?:\s+(?:language|programming|code))?",
        }

        for term, pattern in special_singles.items():
            if re.search(pattern, text):
                results.add(term)

        return results

    def extract_candidates(self, text: str, company: str) -> dict[str, CandidateTerm]:
        """
        Extract all candidate terms from text using all signals.

        Args:
            text: Preprocessed text from job description
            company: Company name for source tracking

        Returns:
            Dictionary mapping normalized term to CandidateTerm
        """
        candidates: dict[str, CandidateTerm] = {}

        def add_candidate(term: str, signal: str, original: str = None):
            """Add or update a candidate term."""
            if not term or len(term) < 2:
                return

            # Normalize: lowercase for key, preserve original
            key = term.lower().strip()
            original = original or term

            if key not in candidates:
                candidates[key] = CandidateTerm(term=term)

            candidates[key].original_forms.add(original)
            candidates[key].sources.add(company)
            candidates[key].count += 1
            candidates[key].signals.add(signal)

        # Apply all extraction signals
        for term in self.extract_camelcase(text):
            add_candidate(term, "camelcase")

        for term in self.extract_allcaps(text):
            add_candidate(term, "allcaps")

        for term in self.extract_special_patterns(text):
            add_candidate(term, "special_pattern")

        for term in self.extract_noun_phrases(text):
            add_candidate(term, "noun_phrase")

        for term in self.extract_from_context(text):
            add_candidate(term, "context")

        for term in self.extract_single_tech_words(text):
            add_candidate(term, "single_word")

        return candidates


def merge_candidates(all_candidates: list[dict[str, CandidateTerm]]) -> dict[str, CandidateTerm]:
    """
    Merge candidate dictionaries from multiple documents.

    Args:
        all_candidates: List of candidate dictionaries from each document

    Returns:
        Merged dictionary with aggregated counts and sources
    """
    merged: dict[str, CandidateTerm] = {}

    for candidates in all_candidates:
        for key, candidate in candidates.items():
            if key not in merged:
                merged[key] = CandidateTerm(
                    term=candidate.term,
                    original_forms=set(candidate.original_forms),
                    sources=set(candidate.sources),
                    count=candidate.count,
                    signals=set(candidate.signals)
                )
            else:
                merged[key].original_forms.update(candidate.original_forms)
                merged[key].sources.update(candidate.sources)
                merged[key].count += candidate.count
                merged[key].signals.update(candidate.signals)

    return merged
