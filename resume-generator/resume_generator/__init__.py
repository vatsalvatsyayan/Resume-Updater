"""
Resume Generator Service.

Standalone service that takes profile data + job description, uses an LLM to
select and tailor content, and produces a tailored resume and PDF.
"""

from .config import ResumeGeneratorConfig
from .generator import generate_resume
from .schemas import ResumeGeneratorInput, TailoredResume

__all__ = [
    "ResumeGeneratorConfig",
    "generate_resume",
    "ResumeGeneratorInput",
    "TailoredResume",
]
