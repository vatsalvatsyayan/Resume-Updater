"""
Abstract LLM provider interface.

Implementations (Gemini, Groq, OpenAI, etc.) can be swapped via config
without changing the tailoring service.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LLMConfig:
    """Configuration for an LLM provider."""

    provider: str
    model: str
    api_key: Optional[str] = None
    max_output_tokens: int = 8192
    temperature: float = 0.3


class LLMProvider(ABC):
    """Abstract interface for text generation. Implement per provider."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate text from the given prompt.

        Returns:
            Generated text. Raises on API/network errors.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name for logging."""
        pass
