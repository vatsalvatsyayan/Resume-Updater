"""
Resume generator configuration.

Model and API keys can be overridden via environment variables so the
service stays model-agnostic and easy to switch.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ResumeGeneratorConfig:
    """Configuration for the resume generator service."""

    llm_provider: str = field(
        default_factory=lambda: os.environ.get("RESUME_LLM_PROVIDER", "gemini")
    )
    llm_model: str = field(
        default_factory=lambda: os.environ.get("RESUME_LLM_MODEL", "gemini-2.0-flash")
    )
    llm_api_key: Optional[str] = field(
        default_factory=lambda: os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    )
    llm_max_output_tokens: int = 8192
    llm_temperature: float = 0.3

    pdf_output_dir: Optional[str] = field(
        default_factory=lambda: os.environ.get("RESUME_PDF_OUTPUT_DIR")
    )

    def llm_config(self) -> "LLMConfig":
        from .llm.base import LLMConfig
        return LLMConfig(
            provider=self.llm_provider,
            model=self.llm_model,
            api_key=self.llm_api_key,
            max_output_tokens=self.llm_max_output_tokens,
            temperature=self.llm_temperature,
        )
