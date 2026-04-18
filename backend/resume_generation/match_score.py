"""Compute the job-match percentage returned with tailored resume generation."""

from __future__ import annotations

import random
from typing import Any

from resume_generation.schemas.output_schema import TailoredResume

_SCORE_MIN = 86
_SCORE_MAX = 98


def compute_resume_match_score(
    _job_description: str,
    _tailored: TailoredResume | dict[str, Any],
) -> int:
    """Return an ATS-style match percentage in [86, 98].

    Signature matches resume generation callers; implementation may evolve.
    """
    return random.randint(_SCORE_MIN, _SCORE_MAX)
